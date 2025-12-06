#!/usr/bin/env python3
"""
Test script to verify variant availability detection logic.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re


def test_variant_detection(url):
    """Test variant detection for a BestBuy product page."""
    driver = None

    try:
        print("=" * 80)
        print("VARIANT AVAILABILITY TEST")
        print("=" * 80)

        # Set up Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(180)

        print(f"\n📍 Loading URL: {url}\n")
        driver.get(url)

        # Wait for page to load
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)

        # Find variant buttons
        variant_buttons = driver.find_elements(By.CSS_SELECTOR, "[class*='openBox'] button")
        print(f"✓ Found {len(variant_buttons)} variant buttons\n")

        results = []

        for idx, button in enumerate(variant_buttons):
            button_text = button.text
            lines = button_text.strip().split('\n')
            variant_name = lines[0].strip() if lines else f"Variant {idx+1}"

            # Extract price from button
            button_price = None
            for line in lines:
                price_match = re.search(r'\$[\d,]+\.?\d*', line)
                if price_match:
                    button_price = price_match.group()
                    break

            print("=" * 80)
            print(f"🔘 Testing variant: {variant_name} ({button_price})")
            print("=" * 80)

            # Click the variant
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)

            # --- TEST 1: Check shipping tiles ---
            print("\n📦 TEST 1: Shipping Tiles")
            print("-" * 80)

            shipping_available = False
            shipping_tiles = driver.find_elements(By.CSS_SELECTOR,
                "button[data-test-id='shipping'], .c-tile button[type='button']")

            for tile in shipping_tiles:
                if tile.is_displayed():
                    tile_text = tile.text
                    tile_class = tile.get_attribute('class') or ''
                    parent = tile.find_element(By.XPATH, "..")
                    parent_class = parent.get_attribute('class') if parent else ''

                    print(f"  Tile found:")
                    print(f"    Text: {repr(tile_text[:100])}")
                    print(f"    Parent classes: {parent_class}")

                    # Check if this is a SELECTED tile (border-selected)
                    is_selected = 'border-selected' in parent_class
                    print(f"    Is selected: {is_selected}")

                    # Check tile text
                    tile_lower = tile_text.lower()
                    has_shipping_keyword = 'shipping' in tile_lower
                    has_delivery_date = any(day in tile_lower for day in ['mon,', 'tue,', 'wed,', 'thu,', 'fri,', 'sat,', 'sun,'])
                    has_unavailable = 'unavailable' in tile_lower

                    print(f"    Has 'shipping': {has_shipping_keyword}")
                    print(f"    Has delivery date: {has_delivery_date}")
                    print(f"    Has 'unavailable': {has_unavailable}")

                    # Available if: selected + has delivery date + no unavailable
                    if is_selected and has_delivery_date and not has_unavailable:
                        shipping_available = True
                        print(f"    ✅ VALID SHIPPING INFO")
                    else:
                        print(f"    ❌ NOT VALID (selected={is_selected}, date={has_delivery_date}, unavailable={has_unavailable})")

            print(f"\n  Final shipping_available: {shipping_available}")

            # --- TEST 2: Check Add to Cart button ---
            print("\n🛒 TEST 2: Add to Cart Button")
            print("-" * 80)

            add_to_cart_enabled = False
            add_to_cart_buttons = driver.find_elements(By.XPATH,
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]")

            for btn in add_to_cart_buttons:
                if btn.is_displayed():
                    is_enabled = btn.is_enabled()
                    btn_class = btn.get_attribute('class') or ''
                    has_disabled_class = 'disabled' in btn_class.lower()

                    print(f"  Button found:")
                    print(f"    Is enabled: {is_enabled}")
                    print(f"    Has disabled class: {has_disabled_class}")
                    print(f"    Classes: {btn_class[:100]}")

                    if is_enabled and not has_disabled_class:
                        add_to_cart_enabled = True
                        print(f"    ✅ ADD TO CART IS ENABLED")
                    else:
                        print(f"    ❌ ADD TO CART IS DISABLED")
                    break

            print(f"\n  Final add_to_cart_enabled: {add_to_cart_enabled}")

            # --- TEST 3: Check for unavailable text in main area ---
            print("\n🚫 TEST 3: Unavailable Text in Main Area")
            print("-" * 80)

            unavailable_in_main = False
            # Look for fulfillment section specifically
            fulfillment_sections = driver.find_elements(By.CSS_SELECTOR,
                "[class*='fulfillment'], [class*='Fulfillment']")

            for section in fulfillment_sections:
                if section.is_displayed():
                    section_text = section.text
                    if 'unavailable' in section_text.lower():
                        print(f"  Found unavailable in fulfillment section:")
                        print(f"    Text: {section_text[:200]}")
                        unavailable_in_main = True
                        break

            print(f"\n  Final unavailable_in_main: {unavailable_in_main}")

            # --- FINAL VERDICT ---
            print("\n" + "=" * 80)
            print("FINAL VERDICT")
            print("=" * 80)

            # Logic: Available if Add to Cart enabled AND shipping available AND not unavailable
            is_available = add_to_cart_enabled and shipping_available and not unavailable_in_main

            print(f"  Add to Cart Enabled: {add_to_cart_enabled}")
            print(f"  Shipping Available: {shipping_available}")
            print(f"  Unavailable in Main: {unavailable_in_main}")
            print(f"\n  {'✅ AVAILABLE' if is_available else '❌ NOT AVAILABLE'}")
            print("=" * 80)
            print()

            results.append({
                'name': variant_name,
                'price': button_price,
                'available': is_available,
                'add_to_cart': add_to_cart_enabled,
                'shipping': shipping_available,
                'unavailable': unavailable_in_main
            })

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        for r in results:
            status = "✅ AVAILABLE" if r['available'] else "❌ UNAVAILABLE"
            print(f"{r['name']:12} {r['price']:12} {status}")
        print("=" * 80)

        return results

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    url = "https://www.bestbuy.com/product/apple-macbook-pro-14-inch-laptop-apple-m4-pro-chip-built-for-apple-intelligence-24gb-memory-512gb-ssd-space-black/JJGCQ8HVWL/sku/6602748/openbox?condition=fair"
    test_variant_detection(url)
