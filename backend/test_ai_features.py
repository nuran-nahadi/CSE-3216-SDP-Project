"""
Test script for AI-powered expense parsing functionality
Run this after setting up the environment and installing dependencies
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import GeminiAIService
from app.core.config import settings


async def test_text_parsing():
    """Test text-based expense parsing"""
    print("🧪 Testing text-based expense parsing...")
    
    if not settings.google_api_key:
        print("❌ Google API key not configured. Please set GOOGLE_API_KEY in your .env file")
        return False
    
    try:
        ai_service = GeminiAIService()
        
        test_cases = [
            "Spent 250 taka on lunch at Pizza Hut today",
            "Bought groceries for 1200 taka at Shwapno using bKash",
            "Paid 500 taka for taxi ride this morning",
            "Coffee at Starbucks 150 taka credit card",
            "Monthly internet bill 1500 taka paid online"
        ]
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n📝 Test case {i}: {text}")
            try:
                result = await ai_service.parse_text_expense(text)
                print(f"✅ Parsed successfully:")
                print(f"   Amount: {result.get('amount')} {result.get('currency', 'Taka')}")
                print(f"   Category: {result.get('category')}")
                print(f"   Merchant: {result.get('merchant', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
            except Exception as e:
                print(f"❌ Failed to parse: {str(e)}")
        
        print("\n✅ Text parsing tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Text parsing test failed: {str(e)}")
        return False


async def test_insights_generation():
    """Test AI insights generation"""
    print("\n🧪 Testing AI insights generation...")
    
    try:
        ai_service = GeminiAIService()
        
        # Mock expense data
        mock_expenses = [
            {"amount": 250, "category": "food", "merchant": "Pizza Hut", "date": "2025-07-10"},
            {"amount": 1200, "category": "shopping", "merchant": "Shwapno", "date": "2025-07-09"},
            {"amount": 500, "category": "transport", "merchant": "Uber", "date": "2025-07-08"},
            {"amount": 150, "category": "food", "merchant": "Starbucks", "date": "2025-07-07"},
            {"amount": 1500, "category": "bills", "merchant": "ISP", "date": "2025-07-06"}
        ]
        
        result = await ai_service.get_spending_insights(mock_expenses)
        
        print("✅ Insights generated successfully:")
        print(f"   Total analyzed expenses: {len(mock_expenses)}")
        print(f"   Insights available: {len(result.get('insights', []))}")
        if 'insights' in result:
            for insight in result['insights'][:3]:  # Show first 3 insights
                print(f"   - {insight}")
        
        print("\n✅ Insights generation test completed")
        return True
        
    except Exception as e:
        print(f"❌ Insights generation test failed: {str(e)}")
        return False


def test_dependencies():
    """Test if all required dependencies are installed"""
    print("🧪 Testing dependencies...")
    
    required_packages = [
        'google.generativeai',
        'PIL',
        'speech_recognition',
        'pydub'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                from PIL import Image
            elif package == 'google.generativeai':
                import google.generativeai as genai
            elif package == 'speech_recognition':
                import speech_recognition as sr
            elif package == 'pydub':
                from pydub import AudioSegment
            print(f"✅ {package} imported successfully")
        except ImportError:
            print(f"❌ {package} not found")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print("pip install google-generativeai Pillow SpeechRecognition pydub ffmpeg-python python-magic")
        return False
    
    print("\n✅ All dependencies are installed")
    return True


def test_configuration():
    """Test configuration setup"""
    print("🧪 Testing configuration...")
    
    if not settings.google_api_key:
        print("❌ GOOGLE_API_KEY not configured")
        print("Please add GOOGLE_API_KEY=your_api_key to your .env file")
        return False
    
    print("✅ Google API key is configured")
    
    # Test other important settings
    if settings.database_url:
        print("✅ Database URL is configured")
    else:
        print("⚠️  Database URL not configured")
    
    return True


async def main():
    """Run all tests"""
    print("🚀 Starting AI Expense Parsing Tests\n")
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency tests failed. Please install missing packages.")
        return
    
    # Test configuration
    if not test_configuration():
        print("\n❌ Configuration tests failed. Please check your .env file.")
        return
    
    # Test AI functionality
    try:
        await test_text_parsing()
        await test_insights_generation()
        
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Start your FastAPI server: uvicorn app.main:app --reload")
        print("2. Test the API endpoints using the examples in AI_EXPENSE_API.md")
        print("3. Integrate with your frontend application")
        
    except Exception as e:
        print(f"\n❌ Tests failed with error: {str(e)}")
        print("Please check your Google API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())
