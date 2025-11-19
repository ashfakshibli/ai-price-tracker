#!/bin/bash
# Heroku Setup Script
# This script helps configure your Heroku app for deployment

set -e  # Exit on error

echo "=================================================="
echo "   AI Price Tracker - Heroku Setup"
echo "=================================================="
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed."
    echo "Install it from: https://devcenter.heroku.com/articles/heroku-cli"
    echo ""
    echo "macOS: brew install heroku/brew/heroku"
    exit 1
fi

echo "✅ Heroku CLI found"
echo ""

# Login to Heroku
echo "📝 Logging into Heroku..."
heroku login

# Get or create app name
echo ""
read -p "Enter your Heroku app name (or press Enter to create a new one): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "Creating a new Heroku app..."
    heroku create
    APP_NAME=$(heroku apps:info --json | python3 -c "import sys, json; print(json.load(sys.stdin)['app']['name'])")
    echo "✅ Created app: $APP_NAME"
else
    # Check if app exists
    if heroku apps:info --app "$APP_NAME" &> /dev/null; then
        echo "✅ Using existing app: $APP_NAME"
    else
        echo "Creating new app: $APP_NAME"
        heroku create "$APP_NAME"
        echo "✅ Created app: $APP_NAME"
    fi
fi

echo ""
echo "=================================================="
echo "   Setting up buildpacks..."
echo "=================================================="

# Clear existing buildpacks
heroku buildpacks:clear --app "$APP_NAME" 2>/dev/null || true

# Add required buildpacks
echo "Adding Python buildpack..."
heroku buildpacks:add heroku/python --app "$APP_NAME"

echo "Adding Google Chrome buildpack..."
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome --app "$APP_NAME"

echo "Adding ChromeDriver buildpack..."
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver --app "$APP_NAME"

echo "✅ Buildpacks configured"
echo ""

# Configure environment variables
echo "=================================================="
echo "   Configuring environment variables..."
echo "=================================================="
echo ""

read -p "Enter your Anthropic API key: " ANTHROPIC_KEY

if [ -z "$ANTHROPIC_KEY" ]; then
    echo "❌ API key is required"
    exit 1
fi

echo "Setting ANTHROPIC_API_KEY..."
heroku config:set ANTHROPIC_API_KEY="$ANTHROPIC_KEY" --app "$APP_NAME"

echo "Generating Flask secret key..."
FLASK_SECRET=$(openssl rand -hex 32)
heroku config:set FLASK_SECRET_KEY="$FLASK_SECRET" --app "$APP_NAME"

echo "✅ Environment variables configured"
echo ""

# Show configuration
echo "=================================================="
echo "   Configuration Summary"
echo "=================================================="
heroku config --app "$APP_NAME"
echo ""

echo "=================================================="
echo "   Buildpacks"
echo "=================================================="
heroku buildpacks --app "$APP_NAME"
echo ""

# Instructions for GitHub Actions
echo "=================================================="
echo "   Next Steps: GitHub Actions CI/CD"
echo "=================================================="
echo ""
echo "To enable automatic deployment from GitHub:"
echo ""
echo "1. Get your Heroku API token:"
echo "   heroku auth:token"
echo ""
echo "2. Add GitHub Secrets (Settings → Secrets → Actions):"
echo "   - HEROKU_API_KEY: (token from step 1)"
echo "   - HEROKU_APP_NAME: $APP_NAME"
echo "   - HEROKU_EMAIL: (your Heroku email)"
echo ""
echo "3. Push to main branch to trigger deployment"
echo ""
echo "=================================================="
echo "   Manual Deployment"
echo "=================================================="
echo ""
echo "To deploy manually right now:"
echo "   git push heroku main"
echo ""
echo "To view logs:"
echo "   heroku logs --tail --app $APP_NAME"
echo ""
echo "To open app:"
echo "   heroku open --app $APP_NAME"
echo ""
echo "✅ Setup complete!"
