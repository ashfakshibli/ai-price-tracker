#!/bin/bash
# Setup cron job for hourly price tracking

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)

echo "🕐 Setting up hourly cron job for price tracking..."
echo ""
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""

# Create the cron command
CRON_CMD="0 * * * * cd $SCRIPT_DIR && $PYTHON_PATH price_tracker.py >> $SCRIPT_DIR/tracker.log 2>&1"

echo "This will add the following cron job:"
echo "$CRON_CMD"
echo ""
read -p "Do you want to add this cron job? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

    if [ $? -eq 0 ]; then
        echo "✅ Cron job added successfully!"
        echo ""
        echo "The price tracker will now run every hour."
        echo "Logs will be saved to: $SCRIPT_DIR/tracker.log"
        echo ""
        echo "To view your cron jobs: crontab -l"
        echo "To remove this cron job: crontab -e (and delete the line)"
    else
        echo "❌ Failed to add cron job"
        exit 1
    fi
else
    echo "Cancelled."
fi
