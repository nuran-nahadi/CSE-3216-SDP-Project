import google.generativeai as genai
from PIL import Image
import speech_recognition as sr
from pydub import AudioSegment
import io
import os
import tempfile
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, UploadFile
import logging

from app.core.config import settings
from app.schemas.expenses import ExpenseCategory, PaymentMethod
from app.schemas.tasks import TaskPriority, TaskStatus
from app.schemas.events import EventBase

logger = logging.getLogger(__name__)


class GeminiAIService:
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.recognizer = sr.Recognizer()
    
    def _get_expense_prompt(self) -> str:
        """Get the prompt template for expense parsing"""
        categories = [cat.value for cat in ExpenseCategory]
        payment_methods = [method.value for method in PaymentMethod]
        
        return f"""
You are an expert expense tracking assistant. Parse the given input and extract expense information.

FIRST, determine if the input is related to an expense, purchase, spending, or financial transaction.
If the input is NOT expense-related (like greetings, random chat, questions, etc.), return:
{{
    "is_expense_related": false,
    "confidence": 0,
    "message": "The input doesn't appear to be expense-related. Please describe a purchase, spending, or financial transaction."
}}

If the input IS expense-related, return a valid JSON object with this structure:
{{
    "is_expense_related": true,
    "amount": float (required),
    "currency": "Taka" (default, or extract if mentioned),
    "category": one of {categories} (required),
    "subcategory": string (optional),
    "merchant": string (optional),
    "description": string (optional),
    "date": "YYYY-MM-DDTHH:MM:SS" (use current date/time if not specified),
    "payment_method": one of {payment_methods} (optional),
    "tags": [list of strings] (optional),
    "confidence": float between 0 and 1
}}

Rules for expense-related inputs:
1. If amount is not clear, return confidence < 0.5
2. Always categorize to the best of your ability
3. Use "other" category only if no other fits
4. Extract merchant name from receipts or context
5. For dates, if only time is mentioned, use today's date
6. For Bangladeshi context: assume Taka currency unless specified otherwise
7. Common payment methods in Bangladesh: bkash, nagad, rocket should map to "digital_wallet"

Examples of expense-related inputs:
- "I spent 500 taka on lunch at KFC"
- "Bought groceries for 1200 taka"
- "Paid electricity bill 800 taka"
- "Coffee 50 taka"
- "Transportation 200"

Examples of NON expense-related inputs:
- "hi there"
- "hello"
- "how are you"
- "what's the weather"
- General conversation

Current date and time: {datetime.now().isoformat()}
"""

    def _get_task_prompt(self) -> str:
        """Get the prompt template for task parsing"""
        priorities = [p.value for p in TaskPriority]
        statuses = [s.value for s in TaskStatus]
        return f"""
You are an expert productivity assistant. Parse the given input and extract task information.

FIRST, determine if the input is related to a task, to-do, reminder, or actionable item.
If the input is NOT task-related (like greetings, random chat, questions, etc.), return:
{{
    "is_task_related": false,
    "confidence": 0,
    "message": "The input doesn't appear to be task-related. Please describe a to-do, reminder, or actionable item."
}}

If the input IS task-related, return a valid JSON object with this structure:
{{
    "is_task_related": true,
    "title": string (required),
    "description": string (optional),
    "due_date": "YYYY-MM-DDTHH:MM:SS" (optional),
    "priority": one of {priorities} (optional, default: medium),
    "status": one of {statuses} (optional, default: pending),
    "tags": [list of strings] (optional),
    "confidence": float between 0 and 1
}}

Rules for task-related inputs:
1. If title is not clear, return confidence < 0.5
2. Always extract due date if mentioned (e.g., today, tomorrow, next week)
3. Use tags if hashtags or keywords are present
4. Default priority is medium, status is pending
5. If the input is a question or greeting, mark is_task_related as false

Examples of task-related inputs:
- "Finish the project report by Friday"
- "Call the bank tomorrow"
- "#work Prepare slides for Monday meeting"
- "Buy groceries"
- "Schedule dentist appointment next week"

Examples of NON task-related inputs:
- "hi there"
- "what's the weather"
- "tell me a joke"
- General conversation

Current date and time: {datetime.now().isoformat()}
"""

    def _get_event_prompt(self) -> str:
        """Get the prompt template for event parsing"""
        return f"""
You are an expert calendar assistant. Parse the given input and extract event information.

FIRST, determine if the input is related to an event, meeting, appointment, or calendar entry.
If the input is NOT event-related (like greetings, random chat, questions, etc.), return:
{{
    \"is_event_related\": false,
    \"confidence\": 0,
    \"message\": \"The input doesn't appear to be event-related. Please describe a meeting, appointment, or calendar event.\"
}}

If the input IS event-related, return a valid JSON object with this structure:
{{
    \"is_event_related\": true,
    \"title\": string (required),
    \"description\": string (optional),
    \"start_time\": \"YYYY-MM-DDTHH:MM:SS\" (required if possible),
    \"end_time\": \"YYYY-MM-DDTHH:MM:SS\" (required if possible),
    \"location\": string (optional),
    \"tags\": [list of strings] (optional),
    \"is_all_day\": bool (optional, default: false),
    \"reminder_minutes\": int (optional),
    \"recurrence_rule\": string (optional),
    \"color\": string (optional, hex color code),
    \"confidence\": float between 0 and 1
}}

Rules for event-related inputs:
1. If title or time is not clear, return confidence < 0.5
2. Always extract start/end time if mentioned (e.g., today, tomorrow, next week, 3pm, etc.)
3. Use tags if hashtags or keywords are present
4. Default is_all_day to false unless clearly all-day
5. If the input is a question or greeting, mark is_event_related as false

Examples of event-related inputs:
- \"Lunch with Sarah at 1pm tomorrow\"
- \"Doctor appointment on Friday at 10am\"
- \"Project meeting next Monday 3-4pm\"
- \"Vacation from July 1st to July 5th\"
- \"All-day conference on 15th\"

Examples of NON event-related inputs:
- \"hi there\"
- \"what's the weather\"
- \"tell me a joke\"
- General conversation

Current date and time: {datetime.now().isoformat()}
"""

    async def parse_text_expense(self, text: str) -> Dict[str, Any]:
        """Parse expense from natural language text"""
        try:
            prompt = self._get_expense_prompt() + f"\n\nInput text: {text}"
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            result = self._extract_json_from_response(response.text)
            
            if not result:
                raise HTTPException(status_code=400, detail="Failed to parse expense from text")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing text expense: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    async def parse_receipt_image(self, image_file: UploadFile) -> Dict[str, Any]:
        """Parse expense from receipt image"""
        try:
            # Read and process image
            image_data = await image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            prompt = self._get_expense_prompt() + """
            
            Analyze this receipt image and extract expense information.
            Look for:
            - Total amount (usually at the bottom)
            - Store/merchant name (usually at the top)
            - Date and time
            - Payment method (if visible)
            - Items purchased to determine category
            
            Focus on the final total amount, not individual item prices.
            """
            
            response = self.model.generate_content([prompt, image])
            
            # Extract JSON from response
            result = self._extract_json_from_response(response.text)
            
            if not result:
                raise HTTPException(status_code=400, detail="Failed to parse expense from receipt")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing receipt image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

    async def parse_voice_expense(self, audio_file: UploadFile) -> Dict[str, Any]:
        """Parse expense from voice recording"""
        try:
            # Read audio file
            audio_data = await audio_file.read()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name
            
            try:
                # Convert to WAV if necessary using pydub
                audio = AudioSegment.from_file(temp_audio_path)
                wav_path = temp_audio_path.replace('.wav', '_converted.wav')
                audio.export(wav_path, format="wav")
                
                # Transcribe audio to text
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                
                # Try Google Speech Recognition first, then fallback to Sphinx
                try:
                    text = self.recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    try:
                        text = self.recognizer.recognize_sphinx(audio_data)
                    except:
                        raise HTTPException(status_code=400, detail="Could not transcribe audio")
                
                logger.info(f"Transcribed text: {text}")
                
                # Parse the transcribed text
                result = await self.parse_text_expense(text)
                result["transcribed_text"] = text
                
                return result
                
            finally:
                # Clean up temporary files
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                wav_path = temp_audio_path.replace('.wav', '_converted.wav')
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                    
        except Exception as e:
            logger.error(f"Error parsing voice expense: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

    async def parse_text_task(self, text: str) -> Dict[str, Any]:
        """Parse task from natural language text"""
        try:
            prompt = self._get_task_prompt() + f"\n\nInput text: {text}"
            response = self.model.generate_content(prompt)
            result = self._extract_json_from_response(response.text, task=True)
            if not result:
                raise HTTPException(status_code=400, detail="Failed to parse task from text")
            return result
        except Exception as e:
            logger.error(f"Error parsing text task: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    async def parse_voice_task(self, audio_file: UploadFile) -> Dict[str, Any]:
        """Parse task from voice recording"""
        try:
            audio_data = await audio_file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name
            try:
                audio = AudioSegment.from_file(temp_audio_path)
                wav_path = temp_audio_path.replace('.wav', '_converted.wav')
                audio.export(wav_path, format="wav")
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                try:
                    text = self.recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    try:
                        text = self.recognizer.recognize_sphinx(audio_data)
                    except:
                        raise HTTPException(status_code=400, detail="Could not transcribe audio")
                logger.info(f"Transcribed text: {text}")
                result = await self.parse_text_task(text)
                result["transcribed_text"] = text
                return result
            finally:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                wav_path = temp_audio_path.replace('.wav', '_converted.wav')
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
        except Exception as e:
            logger.error(f"Error parsing voice task: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

    async def parse_text_event(self, text: str) -> Dict[str, Any]:
        """Parse event from natural language text"""
        try:
            prompt = self._get_event_prompt() + f"\n\nInput text: {text}"
            response = self.model.generate_content(prompt)
            result = self._extract_json_from_response(response.text, event=True)
            if not result:
                raise HTTPException(status_code=400, detail="Failed to parse event from text")
            return result
        except Exception as e:
            logger.error(f"Error parsing text event: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    async def parse_voice_event(self, audio_file: UploadFile) -> Dict[str, Any]:
        """Parse event from voice recording"""
        try:
            audio_data = await audio_file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name
            try:
                audio = AudioSegment.from_file(temp_audio_path)
                wav_path = temp_audio_path.replace('.wav', '_converted.wav')
                audio.export(wav_path, format="wav")
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                try:
                    text = self.recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    try:
                        text = self.recognizer.recognize_sphinx(audio_data)
                    except:
                        raise HTTPException(status_code=400, detail="Could not transcribe audio")
                logger.info(f"Transcribed text: {text}")
                result = await self.parse_text_event(text)
                result["transcribed_text"] = text
                return result
            finally:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                wav_path = temp_audio_path.replace('.wav', '_converted.wav')
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
        except Exception as e:
            logger.error(f"Error parsing voice event: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

    def _extract_json_from_response(self, response_text: str, task: bool = False, event: bool = False) -> Optional[Dict[str, Any]]:
        """Extract JSON object from AI response, with task/expense/event distinction"""
        try:
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response_text)
            cleaned_text = re.sub(r'```\s*|\s*```', '', cleaned_text)
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                if event:
                    if not result.get('is_event_related', True):
                        return {
                            'is_event_related': False,
                            'confidence': 0,
                            'message': result.get('message', "The input doesn't appear to be event-related. Please describe a meeting, appointment, or calendar event.")
                        }
                    if 'title' not in result or not result['title']:
                        logger.error("Missing required fields in AI response (event)")
                        return None
                    if 'confidence' not in result:
                        result['confidence'] = 0.8
                    # Ensure proper date format
                    for time_field in ['start_time', 'end_time']:
                        if time_field in result and result[time_field]:
                            try:
                                dt = datetime.fromisoformat(result[time_field].replace('Z', '+00:00'))
                                result[time_field] = dt.isoformat()
                            except:
                                result[time_field] = None
                    if 'tags' in result and not isinstance(result['tags'], list):
                        try:
                            result['tags'] = json.loads(result['tags'])
                        except:
                            result['tags'] = []
                    return result
                if task:
                    if not result.get('is_task_related', True):
                        return {
                            'is_task_related': False,
                            'confidence': 0,
                            'message': result.get('message', "The input doesn't appear to be task-related. Please describe a to-do, reminder, or actionable item.")
                        }
                    if 'title' not in result or not result['title']:
                        logger.error("Missing required fields in AI response (task)")
                        return None
                    if 'confidence' not in result:
                        result['confidence'] = 0.8
                    # Validate priority
                    valid_priorities = [p.value for p in TaskPriority]
                    if 'priority' in result and result['priority'] not in valid_priorities:
                        result['priority'] = 'medium'
                    # Validate status
                    valid_statuses = [s.value for s in TaskStatus]
                    if 'status' in result and result['status'] not in valid_statuses:
                        result['status'] = 'pending'
                    # Ensure proper date format
                    if 'due_date' in result and result['due_date']:
                        try:
                            dt = datetime.fromisoformat(result['due_date'].replace('Z', '+00:00'))
                            result['due_date'] = dt.isoformat()
                        except:
                            result['due_date'] = None
                    else:
                        result['due_date'] = None
                    if 'tags' in result and not isinstance(result['tags'], list):
                        try:
                            result['tags'] = json.loads(result['tags'])
                        except:
                            result['tags'] = []
                    return result
                else: # Expense parsing
                    # Check if this is a non-expense related response
                    if not result.get('is_expense_related', True):
                        return {
                            'is_expense_related': False,
                            'confidence': 0,
                            'message': result.get('message', 'The input doesn\'t appear to be expense-related. Please describe a purchase, spending, or financial transaction.')
                        }
                    
                    # Validate required fields for expense-related responses
                    if 'amount' not in result or 'category' not in result:
                        logger.error("Missing required fields in AI response")
                        return None
                    
                    # Ensure amount is positive
                    if result['amount'] <= 0:
                        logger.error("Invalid amount in AI response")
                        return None
                    
                    # Set default confidence if not provided
                    if 'confidence' not in result:
                        result['confidence'] = 0.8
                    
                    # Validate category
                    valid_categories = [cat.value for cat in ExpenseCategory]
                    if result['category'] not in valid_categories:
                        result['category'] = 'other'
                    
                    # Validate payment method
                    if 'payment_method' in result and result['payment_method']:
                        valid_methods = [method.value for method in PaymentMethod]
                        if result['payment_method'] not in valid_methods:
                            result['payment_method'] = 'other'
                    
                    # Ensure proper date format
                    if 'date' in result:
                        try:
                            # Try to parse and reformat the date
                            dt = datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
                            result['date'] = dt.isoformat()
                        except:
                            # Use current datetime if parsing fails
                            result['date'] = datetime.now().isoformat()
                    else:
                        result['date'] = datetime.now().isoformat()
                    
                    return result
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return None

    async def get_spending_insights(self, expenses_data: list) -> Dict[str, Any]:
        """Generate AI insights from expense data"""
        try:
            if not expenses_data:
                return {"insights": "No expense data available for analysis."}
            
            # Prepare data summary for AI
            total_amount = sum(exp.get('amount', 0) for exp in expenses_data)
            categories = {}
            for exp in expenses_data:
                cat = exp.get('category', 'other')
                categories[cat] = categories.get(cat, 0) + exp.get('amount', 0)
            
            prompt = f"""
            Analyze the following expense data and provide insights in JSON format:
            
            Total spending: {total_amount} Taka
            Category breakdown: {json.dumps(categories, indent=2)}
            Number of transactions: {len(expenses_data)}
            
            Provide insights in this JSON format:
            {{
                "total_spending": {total_amount},
                "top_category": "category_name",
                "top_category_amount": amount,
                "insights": [
                    "Brief insight 1",
                    "Brief insight 2",
                    "Brief insight 3"
                ],
                "recommendations": [
                    "Brief recommendation 1",
                    "Brief recommendation 2"
                ],
                "spending_trend": "increasing/decreasing/stable"
            }}
            
            Focus on:
            1. Spending patterns
            2. Budget optimization suggestions
            3. Unusual spending alerts
            4. Category-wise analysis
            """
            
            response = self.model.generate_content(prompt)
            result = self._extract_json_from_response(response.text)
            
            return result if result else {"insights": "Unable to generate insights at this time."}
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {"insights": f"Error generating insights: {str(e)}"}


# Create singleton instance
ai_service = GeminiAIService()
