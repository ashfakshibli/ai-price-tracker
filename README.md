# AI Price Tracker

A simple price tracking tool that monitors product prices and availability on web pages.

## Features

- Tracks product prices, variants, and availability
- Uses Claude AI to intelligently extract product information
- Stores historical data to detect changes
- Terminal notifications for price drops or availability changes
- Easy to run via cron for hourly checks

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

3. Configure products to track in `config.json`

4. Run the tracker:
```bash
python price_tracker.py
```

## Running Hourly (macOS/Linux)

Add to your crontab:
```bash
# Run every hour
0 * * * * cd /path/to/ai-price-tracker && /usr/bin/python3 price_tracker.py >> tracker.log 2>&1
```

## Configuration

Edit `config.json` to add products to track:
```json
{
  "products": [
    {
      "name": "MacBook Pro 14 - Fair Condition",
      "url": "https://www.bestbuy.com/...",
      "notify_on_price_drop": true,
      "notify_on_availability": true
    }
  ]
}
```

## Output

- Tracked data is stored in `data/` directory
- Each product gets its own JSON file with historical data
- Notifications are printed to terminal (can be extended for email)
