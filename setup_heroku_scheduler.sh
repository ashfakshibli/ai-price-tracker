#!/bin/bash
# Setup Heroku Scheduler for AI Price Tracker
# This script helps you configure automated price tracking on Heroku

set -e

APP_NAME="${1:-ai-price-tracker}"

echo "🚀 Setting up Heroku Scheduler for $APP_NAME"
echo ""

# Check if scheduler is installed
echo "📦 Checking if Scheduler addon is installed..."
if heroku addons --app "$APP_NAME" | grep -q scheduler; then
    echo "✓ Scheduler addon is already installed"
else
    echo "📥 Installing Scheduler addon..."
    heroku addons:create scheduler:standard --app "$APP_NAME"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Open the Scheduler dashboard:"
echo "   heroku addons:open scheduler --app $APP_NAME"
echo ""
echo "2. In the dashboard:"
echo "   - Click 'Create job'"
echo "   - Set frequency (e.g., 'Every hour')"
echo "   - Enter command: python price_tracker.py"
echo "   - Click 'Save job'"
echo ""
echo "3. Verify the job is running:"
echo "   heroku logs --tail --app $APP_NAME | grep 'price_tracker'"
echo ""
echo "🎉 Your app is now ready for automated price tracking!"
echo ""

# Optionally open the scheduler dashboard
read -p "Would you like to open the Scheduler dashboard now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    heroku addons:open scheduler --app "$APP_NAME"
fi
