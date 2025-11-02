# AI-Powered Expense Tracking API

This document describes the AI-powered features for automatic expense data entry using Google's Gemini Flash API.

## Overview

The system supports three methods of AI-powered expense entry:
1. **Text Input**: Natural language text parsing
2. **Receipt Images**: OCR and analysis of receipt photos
3. **Voice Input**: Speech-to-text transcription followed by text parsing

## Features

### 1. Text-based Expense Parsing
Parse natural language descriptions into structured expense data.

**Endpoint**: `POST /expenses/ai/parse-text`

**Example inputs**:
- "Spent 250 taka on lunch at Pizza Hut today"
- "Bought groceries for 1200 taka at Shwapno using bKash"
- "Paid 500 taka for taxi ride this morning"

**Request**:
```json
{
  "text": "Spent 250 taka on lunch at Pizza Hut today"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "expense-uuid",
    "amount": 250.0,
    "currency": "Taka",
    "category": "food",
    "merchant": "Pizza Hut",
    "description": "lunch",
    "date": "2025-07-10T12:30:00",
    "payment_method": null,
    "tags": ["lunch"],
    ...
  },
  "parsed_data": {
    "amount": 250.0,
    "currency": "Taka",
    "category": "food",
    "merchant": "Pizza Hut",
    "description": "lunch",
    "date": "2025-07-10T12:30:00",
    "confidence": 0.95
  },
  "confidence": 0.95,
  "message": "Expense created successfully from text"
}
```

### 2. Receipt Image Processing
Analyze receipt images to extract expense information.

**Endpoint**: `POST /expenses/ai/parse-receipt`

**Supported formats**: JPG, PNG, WEBP, GIF
**Max file size**: 5MB

**Request**: Multipart form data with image file

**Response**: Similar to text parsing, with extracted receipt data

### 3. Voice Recording Processing
Convert speech to text, then parse as expense data.

**Endpoint**: `POST /expenses/ai/parse-voice`

**Supported formats**: MP3, WAV, M4A
**Max file size**: 10MB (configurable)

**Response**: Similar to text parsing, includes `transcribed_text` field

### 4. AI Spending Insights
Get AI-powered analysis of spending patterns and recommendations.

**Endpoint**: `GET /expenses/ai/insights?days=30`

**Parameters:**
- `days` (integer, optional, default: 30, min: 1, max: 365): Number of days to analyze for insights.

**Description:**
This endpoint analyzes your recent expenses using AI to provide personalized insights, spending patterns, and actionable recommendations. The analysis covers the specified number of days (default: 30). Insights may include top spending categories, trend analysis, budget suggestions, and unusual spending alerts. The response includes a summary, recommendations, and trend information.

**Response Example:**
```json
{
  "success": true,
  "data": {
    "total_spending": 15000.0,
    "top_category": "food",
    "top_category_amount": 6000.0,
    "insights": [
      "Your food spending increased by 20% this month",
      "Most expenses occur on weekends",
      "Digital wallet usage is trending upward"
    ],
    "recommendations": [
      "Consider setting a daily food budget of 200 Taka",
      "Try meal planning to reduce impulse food purchases"
    ],
    "spending_trend": "increasing"
  },
  "message": "AI insights generated successfully"
}
```

If there are no expenses in the selected period, the response will indicate that no data is available:
```json
{
  "success": true,
  "data": { "insights": "No recent expenses found for analysis." },
  "message": "No data available for insights"
}
```

**Rate Limit:** 5 requests/minute per user

**Best Practices:**
- Use this endpoint to help users understand their spending habits and receive actionable suggestions.
- Encourage users to review insights regularly for better financial awareness.
- If no data is available, prompt users to add expenses for more meaningful analysis.

## Configuration

### Environment Variables
Add to your `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Dependencies
The following packages are required:
```
google-generativeai
Pillow
SpeechRecognition
pydub
ffmpeg-python
python-magic
```

## Implementation Details

### AI Service
- Uses Google's Gemini 1.5 Flash model for text and image analysis
- Includes speech recognition for voice inputs
- Provides confidence scoring for parsed data
- Handles Bangladesh-specific context (Taka currency, local payment methods)

### Confidence Scoring
- Responses include confidence scores (0.0 to 1.0)
- Low confidence (< 0.5) returns parsed data without creating expense
- Users can review and manually adjust low-confidence parses

### Error Handling
- Graceful degradation when AI services are unavailable
- Detailed error messages for troubleshooting
- Fallback to manual entry when parsing fails

### Security
- File type validation for uploads
- Size limits on uploaded files
- Input sanitization and validation

## Usage Examples

### Frontend Integration

**Text Input**:
```javascript
const parseExpense = async (text) => {
  const response = await fetch('/api/expenses/ai/parse-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text })
  });
  return response.json();
};
```

**Receipt Upload**:
```javascript
const parseReceipt = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('/api/expenses/ai/parse-receipt', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  return response.json();
};
```

**Voice Recording**:
```javascript
const parseVoice = async (audioFile) => {
  const formData = new FormData();
  formData.append('file', audioFile);
  
  const response = await fetch('/api/expenses/ai/parse-voice', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  return response.json();
};
```

## Best Practices

1. **Input Quality**: Encourage clear, descriptive input for better parsing accuracy
2. **Confidence Thresholds**: Review low-confidence parses before accepting
3. **Fallback Options**: Always provide manual entry as an alternative
4. **User Feedback**: Allow users to correct AI mistakes to improve future parsing
5. **Privacy**: Ensure sensitive financial data is handled securely

## Troubleshooting

### Common Issues

1. **Low confidence scores**: Input may be ambiguous or unclear
2. **Category misclassification**: AI may need more context about spending patterns
3. **Amount extraction errors**: Ensure amounts are clearly stated in input
4. **Receipt processing failures**: Check image quality and clarity

### Performance Optimization

1. **Caching**: Cache AI responses for identical inputs
2. **Batch Processing**: Process multiple receipts in batches when possible
3. **Async Processing**: Use background tasks for heavy AI operations
4. **Rate Limiting**: Implement rate limits to manage API costs

## API Rate Limits

- Text parsing: 60 requests/minute per user
- Image processing: 20 requests/minute per user  
- Voice processing: 10 requests/minute per user
- Insights generation: 5 requests/minute per user

## Cost Considerations

- Monitor Gemini API usage and costs
- Implement usage analytics and alerts
- Consider caching strategies to reduce API calls
- Set up billing alerts for API consumption
