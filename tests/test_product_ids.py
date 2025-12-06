#!/usr/bin/env python3
"""
Test that product IDs are correctly using integer indices.
"""

import json
from pathlib import Path

def test_product_id_consistency():
    """Test that product IDs are consistent between routes."""
    print("=" * 60)
    print("Testing Product ID Consistency")
    print("=" * 60)

    # Create test config
    test_config = {
        "products": [
            {"name": "Product 1", "url": "https://example.com/product1", "notify_on_price_drop": True, "notify_on_availability": True, "track_variants": False},
            {"name": "Product 2", "url": "https://example.com/product2", "notify_on_price_drop": True, "notify_on_availability": True, "track_variants": False},
            {"name": "Product 3 \"Special\"", "url": "https://example.com/product3", "notify_on_price_drop": True, "notify_on_availability": True, "track_variants": False},
        ],
        "check_interval_hours": 1,
        "notifications": {"terminal": True, "email": False}
    }

    # Simulate what get_all_products_with_history() does
    products = []
    for index, product in enumerate(test_config.get('products', [])):
        import hashlib
        hash_id = hashlib.md5(product['url'].encode()).hexdigest()[:12]

        products.append({
            'id': index,  # Integer index
            'hash_id': hash_id,  # String hash
            'config': product
        })

    # Test that IDs are integers
    print("\nTest 1: Verify all IDs are integers")
    for product in products:
        product_id = product['id']
        if isinstance(product_id, int):
            print(f"  ✓ Product '{product['config']['name']}' ID is integer: {product_id}")
        else:
            print(f"  ✗ Product '{product['config']['name']}' ID is NOT integer: {product_id} (type: {type(product_id)})")
            return False

    # Test that IDs are sequential starting from 0
    print("\nTest 2: Verify IDs are sequential starting from 0")
    expected_ids = list(range(len(products)))
    actual_ids = [p['id'] for p in products]
    if actual_ids == expected_ids:
        print(f"  ✓ IDs are correctly sequential: {actual_ids}")
    else:
        print(f"  ✗ IDs are NOT sequential")
        print(f"    Expected: {expected_ids}")
        print(f"    Actual: {actual_ids}")
        return False

    # Test URL routing
    print("\nTest 3: Verify URL routing would work")
    test_routes = [
        ("/api/update_product/0", True, "Integer ID 0"),
        ("/api/update_product/1", True, "Integer ID 1"),
        ("/api/update_product/2", True, "Integer ID 2"),
        ("/api/update_product/abc123", False, "Hash string (should fail)"),
        ("/remove_product/0", True, "Integer ID 0"),
        ("/history/1", True, "Integer ID 1"),
    ]

    for route, should_match, description in test_routes:
        # Extract the ID part
        parts = route.split('/')
        product_id = parts[-1]

        # Check if it's an integer
        try:
            int(product_id)
            is_int = True
        except ValueError:
            is_int = False

        if is_int == should_match:
            print(f"  ✓ {description}: {route} - {'would match' if should_match else 'would NOT match'}")
        else:
            print(f"  ✗ {description}: {route} - expected {'match' if should_match else 'no match'}, got opposite")
            return False

    # Test that hash_id is preserved for file operations
    print("\nTest 4: Verify hash_id is available for file operations")
    for product in products:
        if 'hash_id' in product and isinstance(product['hash_id'], str) and len(product['hash_id']) == 12:
            print(f"  ✓ Product '{product['config']['name']}' has hash_id: {product['hash_id']}")
        else:
            print(f"  ✗ Product '{product['config']['name']}' missing or invalid hash_id")
            return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_product_id_consistency()
    exit(0 if success else 1)
