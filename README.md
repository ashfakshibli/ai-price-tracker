# AI Price Tracker

A simple price tracking tool that monitors product prices and availability on web pages.

## Features

- **Real browser automation** using Selenium for JavaScript-heavy sites
- Waits for pages to fully load before extracting data
- Tracks product prices, variants, and availability
- Uses Claude AI to intelligently extract product information from rendered HTML
- Stores historical data to detect changes
- Terminal notifications for price drops or availability changes
- Robust retry logic with 3-minute timeout for slow-loading sites
- Automatic retry with exponential backoff on failures
- Headless mode (no visible browser window)
- Easy to run via cron for hourly checks

## Setup

### Prerequisites

- **Chrome browser** must be installed (used for headless browsing)
- **Python 3.8+**
- **Anthropic API key** (get one from https://console.anthropic.com/)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

The first run will automatically download the appropriate ChromeDriver for your system.

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or add it to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
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

## How It Works

1. **Browser Automation**: Uses Selenium with Chrome in headless mode to load pages
2. **JavaScript Rendering**: Waits for JavaScript to execute and content to load
3. **Smart Waiting**: Detects when price elements appear on the page
4. **AI Extraction**: Claude AI analyzes the fully rendered HTML to extract product data
5. **Change Detection**: Compares with historical data to detect price drops or availability changes
6. **Notifications**: Alerts you via terminal when changes are detected

## Troubleshooting

### Slow Websites (BestBuy, etc.)

The tracker uses **real browser automation** to handle JavaScript-heavy sites:
- **Page load timeout**: 180 seconds (3 minutes)
- **Smart waiting**: Waits for price elements to appear (up to 20 seconds)
- **Retries**: Up to 3 attempts with progressive delays (5s, 10s, 15s)
- **Total time**: Up to 9 minutes for very slow sites

### Chrome/ChromeDriver Issues

If you get driver errors:
```bash
# Update pip packages
pip install --upgrade selenium webdriver-manager

# The ChromeDriver will auto-download on first run
```

### Common Issues

1. **"Chrome not found"**: Make sure Google Chrome is installed
2. **Timeouts**: Check your internet connection and try accessing the URL in your browser
3. **No price detected**: The website structure may have changed; check the `data/` folder for what was captured
