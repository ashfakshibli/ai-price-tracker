#!/usr/bin/env python3
"""
AI-powered price tracker for monitoring product prices and availability.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic


class PriceTracker:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the price tracker."""
        self.config = self._load_config(config_path)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _get_product_id(self, url: str) -> str:
        """Generate a unique ID for a product based on its URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def _fetch_webpage(self, url: str, max_retries: int = 3) -> str:
        """Fetch webpage content with retry logic for slow-loading sites."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        for attempt in range(max_retries):
            try:
                print(f"⏳ Fetching webpage... (attempt {attempt + 1}/{max_retries})")
                # Increased timeout to 180 seconds (3 minutes) for slow sites like BestBuy
                response = requests.get(url, headers=headers, timeout=180)
                response.raise_for_status()
                print(f"✓ Successfully fetched webpage ({len(response.text)} bytes)")
                return response.text
            except requests.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)  # Progressive delay: 5s, 10s, 15s
                    print(f"⏱️  Request timed out. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Error: Request timed out after {max_retries} attempts")
                    print(f"   The website is taking too long to respond (>180 seconds)")
                    return None
            except requests.RequestException as e:
                print(f"❌ Error fetching {url}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"   Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    return None

        return None

    def _extract_product_data(self, html: str, url: str, product_name: str) -> Optional[Dict]:
        """Use Claude AI to extract product data from HTML."""
        # Get the main content using BeautifulSoup to reduce token usage
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style tags
        for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
            tag.decompose()

        # Get text content (first 50000 chars to avoid token limits)
        text_content = soup.get_text(separator='\n', strip=True)[:50000]

        prompt = f"""You are analyzing a product page to extract pricing and availability information.

Product URL: {url}
Product Name: {product_name}

Please analyze the following page content and extract:
1. Current price (as a number, without currency symbol)
2. Currency (USD, EUR, etc.)
3. Available variants (e.g., conditions like "Fair", "Good", "Excellent" or sizes/colors)
4. For each variant: name, price, and whether it's in stock/available
5. Whether the product can be added to cart (is available for purchase)

Page content:
{text_content}

Respond ONLY with a valid JSON object in this exact format:
{{
  "product_name": "extracted product name",
  "price": 999.99,
  "currency": "USD",
  "in_stock": true,
  "can_add_to_cart": true,
  "variants": [
    {{"name": "Fair", "price": 899.99, "available": false}},
    {{"name": "Good", "price": 999.99, "available": true}}
  ],
  "extracted_at": "{datetime.now().isoformat()}"
}}

If information is not found, use null for that field. Be precise with numbers.
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = message.content[0].text.strip()

            # Try to extract JSON if it's wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            data = json.loads(response_text)
            data['url'] = url
            data['checked_at'] = datetime.now().isoformat()

            return data

        except Exception as e:
            print(f"❌ Error extracting data with AI: {e}")
            return None

    def _load_previous_data(self, product_id: str) -> Optional[Dict]:
        """Load previous tracking data for a product."""
        data_file = self.data_dir / f"{product_id}.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                return json.load(f)
        return None

    def _save_data(self, product_id: str, data: Dict):
        """Save tracking data for a product."""
        data_file = self.data_dir / f"{product_id}.json"

        # Load history
        history = []
        if data_file.exists():
            with open(data_file, 'r') as f:
                existing = json.load(f)
                history = existing.get('history', [])

        # Add current data to history
        history.append(data)

        # Keep last 100 entries
        history = history[-100:]

        # Save
        with open(data_file, 'w') as f:
            json.dump({
                'current': data,
                'history': history
            }, f, indent=2)

    def _compare_and_notify(self, product_config: Dict, current: Dict, previous: Optional[Dict]):
        """Compare current and previous data and send notifications."""
        if previous is None:
            print(f"\n📊 First time tracking: {product_config['name']}")
            self._print_product_info(current)
            return

        notifications = []

        # Check price changes
        if product_config.get('notify_on_price_drop', True):
            if current.get('price') and previous.get('price'):
                if current['price'] < previous['price']:
                    diff = previous['price'] - current['price']
                    notifications.append(
                        f"💰 Price dropped: ${previous['price']:.2f} → ${current['price']:.2f} (saved ${diff:.2f})"
                    )

        # Check availability changes
        if product_config.get('notify_on_availability', True):
            prev_available = previous.get('can_add_to_cart', False)
            curr_available = current.get('can_add_to_cart', False)

            if curr_available and not prev_available:
                notifications.append("✅ Now available to purchase!")

        # Check variant availability
        if product_config.get('track_variants', True):
            prev_variants = {v['name']: v for v in previous.get('variants', [])}
            curr_variants = {v['name']: v for v in current.get('variants', [])}

            for name, curr_variant in curr_variants.items():
                prev_variant = prev_variants.get(name)

                # New variant became available
                if curr_variant.get('available'):
                    if not prev_variant or not prev_variant.get('available'):
                        notifications.append(
                            f"🎯 Variant '{name}' now available at ${curr_variant.get('price', 'N/A')}"
                        )
                    # Variant price dropped
                    elif prev_variant and prev_variant.get('price') and curr_variant.get('price'):
                        if curr_variant['price'] < prev_variant['price']:
                            diff = prev_variant['price'] - curr_variant['price']
                            notifications.append(
                                f"💲 Variant '{name}' price dropped: ${prev_variant['price']:.2f} → ${curr_variant['price']:.2f} (saved ${diff:.2f})"
                            )

        # Send notifications
        if notifications:
            print(f"\n🔔 ALERTS for {product_config['name']}:")
            print("=" * 60)
            for notification in notifications:
                print(f"  {notification}")
            print("=" * 60)
            self._print_product_info(current)
        else:
            print(f"\n✓ No changes detected for: {product_config['name']}")

    def _print_product_info(self, data: Dict):
        """Print product information."""
        print(f"\nProduct: {data.get('product_name', 'Unknown')}")
        print(f"Price: ${data.get('price', 'N/A')} {data.get('currency', '')}")
        print(f"In Stock: {'✅ Yes' if data.get('in_stock') else '❌ No'}")
        print(f"Can Add to Cart: {'✅ Yes' if data.get('can_add_to_cart') else '❌ No'}")

        if data.get('variants'):
            print("\nVariants:")
            for variant in data['variants']:
                status = "✅ Available" if variant.get('available') else "❌ Unavailable"
                price = f"${variant.get('price', 'N/A')}"
                print(f"  - {variant['name']}: {price} - {status}")

        print(f"\nLast checked: {data.get('checked_at', 'Unknown')}")

    def track_all_products(self):
        """Track all configured products."""
        products = self.config.get('products', [])

        if not products:
            print("⚠️  No products configured in config.json")
            return

        print(f"🔍 Tracking {len(products)} product(s)...")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        for product_config in products:
            url = product_config['url']
            product_id = self._get_product_id(url)

            print(f"\n{'='*60}")
            print(f"Checking: {product_config['name']}")
            print(f"{'='*60}")

            # Fetch webpage
            html = self._fetch_webpage(url)
            if not html:
                continue

            # Extract data using AI
            current_data = self._extract_product_data(
                html,
                url,
                product_config['name']
            )

            if not current_data:
                continue

            # Load previous data
            previous_data = self._load_previous_data(product_id)
            if previous_data:
                previous_data = previous_data.get('current')

            # Compare and notify
            self._compare_and_notify(product_config, current_data, previous_data)

            # Save new data
            self._save_data(product_id, current_data)

        print(f"\n✅ Tracking completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main entry point."""
    try:
        tracker = PriceTracker()
        tracker.track_all_products()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tracking interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
