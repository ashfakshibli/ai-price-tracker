#!/bin/bash
# Setup script for AI Price Tracker

echo "🚀 Setting up AI Price Tracker..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment (optional but recommended)
read -p "Do you want to create a virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  ANTHROPIC_API_KEY environment variable is not set"
    echo ""
    echo "To set it:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to your ~/.bashrc or ~/.zshrc:"
    echo "  echo 'export ANTHROPIC_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
    echo ""
else
    echo "✓ ANTHROPIC_API_KEY is set"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set your ANTHROPIC_API_KEY if you haven't already"
echo "  2. Edit config.json to add products to track"
echo "  3. Run: python3 price_tracker.py"
echo ""
echo "To set up hourly tracking, run:"
echo "  ./setup_cron.sh"
echo ""
