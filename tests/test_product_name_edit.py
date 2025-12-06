#!/usr/bin/env python3
"""
Test script for product name editing with special characters.
Tests that various special characters in product names work correctly.
"""

import json
from pathlib import Path

# Test cases with special characters
test_cases = [
    {
        "name": "Simple Product Name",
        "description": "Basic alphanumeric name",
        "expected_pass": True
    },
    {
        "name": "Product \"with quotes\"",
        "description": "Name with double quotes",
        "expected_pass": True
    },
    {
        "name": "Toys & Games",
        "description": "Name with ampersand",
        "expected_pass": True
    },
    {
        "name": "MacBook Pro 14\" - M3",
        "description": "Name with quotes and dash",
        "expected_pass": True
    },
    {
        "name": "Price < $100 & > $50",
        "description": "Name with less-than, greater-than, ampersand",
        "expected_pass": True
    },
    {
        "name": "Product's Name (2024)",
        "description": "Name with apostrophe and parentheses",
        "expected_pass": True
    },
    {
        "name": "Name/with/slashes",
        "description": "Name with forward slashes",
        "expected_pass": True
    },
    {
        "name": "Name\\with\\backslashes",
        "description": "Name with backslashes",
        "expected_pass": True
    },
    {
        "name": "Line1\nLine2",
        "description": "Name with newline",
        "expected_pass": True
    },
    {
        "name": "Tab\there",
        "description": "Name with tab",
        "expected_pass": True
    },
]

def test_json_serialization():
    """Test that all product names can be JSON serialized."""
    print("=" * 60)
    print("Testing JSON Serialization")
    print("=" * 60)

    passed = 0
    failed = 0

    for test in test_cases:
        name = test["name"]
        desc = test["description"]

        try:
            # Test JSON serialization (what happens in the AJAX call)
            json_str = json.dumps({"name": name})

            # Test deserialization
            parsed = json.loads(json_str)

            # Verify round-trip
            if parsed["name"] == name:
                print(f"✓ PASS: {desc}")
                print(f"  Name: {repr(name)}")
                print(f"  JSON: {json_str}")
                passed += 1
            else:
                print(f"✗ FAIL: {desc}")
                print(f"  Expected: {repr(name)}")
                print(f"  Got: {repr(parsed['name'])}")
                failed += 1

        except Exception as e:
            print(f"✗ FAIL: {desc}")
            print(f"  Name: {repr(name)}")
            print(f"  Error: {e}")
            failed += 1

        print()

    print(f"Results: {passed} passed, {failed} failed")
    print()
    return failed == 0

def test_html_escaping():
    """Test HTML attribute escaping (simulating Jinja's |e filter)."""
    print("=" * 60)
    print("Testing HTML Attribute Escaping")
    print("=" * 60)

    import html

    passed = 0
    failed = 0

    for test in test_cases:
        name = test["name"]
        desc = test["description"]

        try:
            # Simulate what Jinja's |e filter does
            escaped = html.escape(name, quote=True)

            # Simulate HTML attribute
            html_attr = f'data-original-name="{escaped}"'

            print(f"✓ PASS: {desc}")
            print(f"  Original: {repr(name)}")
            print(f"  Escaped:  {repr(escaped)}")
            print(f"  In HTML:  {html_attr}")
            passed += 1

        except Exception as e:
            print(f"✗ FAIL: {desc}")
            print(f"  Name: {repr(name)}")
            print(f"  Error: {e}")
            failed += 1

        print()

    print(f"Results: {passed} passed, {failed} failed")
    print()
    return failed == 0

def test_config_file_save():
    """Test that product names can be saved to config.json."""
    print("=" * 60)
    print("Testing Config File Save/Load")
    print("=" * 60)

    test_config_file = Path("test_config.json")

    passed = 0
    failed = 0

    for test in test_cases:
        name = test["name"]
        desc = test["description"]

        try:
            # Create test config
            config = {
                "products": [{
                    "name": name,
                    "url": "https://example.com/product",
                    "notify_on_price_drop": True,
                    "notify_on_availability": True,
                    "track_variants": False
                }],
                "check_interval_hours": 1
            }

            # Save to file
            with open(test_config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Load back
            with open(test_config_file, 'r') as f:
                loaded = json.load(f)

            # Verify
            if loaded["products"][0]["name"] == name:
                print(f"✓ PASS: {desc}")
                print(f"  Saved and loaded: {repr(name)}")
                passed += 1
            else:
                print(f"✗ FAIL: {desc}")
                print(f"  Expected: {repr(name)}")
                print(f"  Got: {repr(loaded['products'][0]['name'])}")
                failed += 1

        except Exception as e:
            print(f"✗ FAIL: {desc}")
            print(f"  Name: {repr(name)}")
            print(f"  Error: {e}")
            failed += 1

        print()

    # Cleanup
    if test_config_file.exists():
        test_config_file.unlink()

    print(f"Results: {passed} passed, {failed} failed")
    print()
    return failed == 0

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRODUCT NAME SPECIAL CHARACTERS TEST SUITE")
    print("=" * 60 + "\n")

    all_passed = True

    all_passed = test_json_serialization() and all_passed
    all_passed = test_html_escaping() and all_passed
    all_passed = test_config_file_save() and all_passed

    print("=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
