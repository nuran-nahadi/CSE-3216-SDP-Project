#!/bin/bash

# AI Expense Tracking Setup Script
# This script helps set up the AI-powered expense tracking features

echo "🚀 Setting up AI-powered Expense Tracking..."
echo "================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
echo "📋 Checking Python installation..."
if command_exists python3; then
    python_version=$(python3 --version)
    echo "✅ Found: $python_version"
else
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check pip installation
echo "📋 Checking pip installation..."
if command_exists pip3; then
    echo "✅ pip3 is available"
elif command_exists pip; then
    echo "✅ pip is available"
else
    echo "❌ pip is required but not installed."
    echo "Please install pip and try again."
    exit 1
fi

# Install system dependencies for audio processing
echo "📋 Installing system dependencies..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command_exists brew; then
        echo "Installing ffmpeg and other dependencies via Homebrew..."
        brew install ffmpeg portaudio
    else
        echo "⚠️  Homebrew not found. Please install ffmpeg manually:"
        echo "   1. Install Homebrew: https://brew.sh/"
        echo "   2. Run: brew install ffmpeg portaudio"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command_exists apt-get; then
        echo "Installing dependencies via apt..."
        sudo apt-get update
        sudo apt-get install -y ffmpeg portaudio19-dev python3-pyaudio
    elif command_exists yum; then
        echo "Installing dependencies via yum..."
        sudo yum install -y ffmpeg portaudio-devel
    else
        echo "⚠️  Please install ffmpeg and portaudio manually for your Linux distribution"
    fi
else
    echo "⚠️  Unsupported OS. Please install ffmpeg and portaudio manually."
fi

# Install Python packages
echo "📦 Installing Python packages..."
echo "This may take a few minutes..."

pip3 install -r requirements.txt

# Additional packages for AI features
echo "📦 Installing additional AI packages..."
pip3 install google-generativeai Pillow SpeechRecognition pydub ffmpeg-python python-magic

# Check if .env file exists
echo "📋 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - GOOGLE_API_KEY: Your Google Gemini API key"
    echo "   - Database credentials"
    echo "   - Other required settings"
else
    echo "✅ .env file already exists"
fi

# Test the installation
echo "🧪 Testing AI features..."
python3 test_ai_features.py

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit your .env file with the required API keys"
echo "2. Set up your database (run migrations if needed)"
echo "3. Start the server: uvicorn app.main:app --reload"
echo "4. Test the AI endpoints using the API documentation"
echo ""
echo "📚 Documentation:"
echo "- API docs: apidocs/AI_EXPENSE_API.md"
echo "- Test script: python3 test_ai_features.py"
echo ""
echo "💡 Get your Google Gemini API key at:"
echo "   https://makersuite.google.com/app/apikey"
