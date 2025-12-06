#!/usr/bin/env python3
"""
Test product sorting by creation time.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


def test_product_sorting():
    """Test that products are sorted by creation time (newest first)."""
    print("=" * 60)
    print("Testing Product Sorting")
    print("=" * 60)

    # Create test products with different timestamps
    now = datetime.now()
    products = [
        {
            'name': 'Product 1 (oldest)',
            'url': 'https://example.com/1',
            'created_at': (now - timedelta(days=3)).isoformat()
        },
        {
            'name': 'Product 2 (newest)',
            'url': 'https://example.com/2',
            'created_at': now.isoformat()
        },
        {
            'name': 'Product 3 (middle)',
            'url': 'https://example.com/3',
            'created_at': (now - timedelta(days=1)).isoformat()
        },
        {
            'name': 'Product 4 (no timestamp)',
            'url': 'https://example.com/4',
            # No created_at field
        }
    ]

    print("\nOriginal order:")
    for i, p in enumerate(products):
        created = p.get('created_at', 'No timestamp')
        print(f"  {i}: {p['name']} - {created}")

    # Simulate the sorting logic from get_all_products_with_history()
    # Create product objects similar to what the function returns
    product_objects = []
    for index, product in enumerate(products):
        product_objects.append({
            'id': index,
            'config': product,
            'created_at': product.get('created_at')
        })

    # Sort by creation time, newest first
    product_objects.sort(key=lambda p: p['created_at'] or '', reverse=True)

    print("\nSorted order (newest first):")
    for i, p in enumerate(product_objects):
        created = p['created_at'] or 'No timestamp'
        print(f"  {i}: {p['config']['name']} - {created}")
        print(f"      Original ID: {p['id']}")

    # Verify the order
    expected_order = [
        'Product 2 (newest)',
        'Product 3 (middle)',
        'Product 1 (oldest)',
        'Product 4 (no timestamp)'
    ]

    actual_order = [p['config']['name'] for p in product_objects]

    print("\nVerification:")
    all_passed = True
    for i, (expected, actual) in enumerate(zip(expected_order, actual_order)):
        if expected == actual:
            print(f"  ✓ Position {i}: {actual}")
        else:
            print(f"  ✗ Position {i}: Expected '{expected}', got '{actual}'")
            all_passed = False

    # Test that original IDs are preserved
    print("\nID Preservation Test:")
    print("  Product 2 (index 1) should still have id=1:", product_objects[0]['id'] == 1)
    print("  Product 3 (index 2) should still have id=2:", product_objects[1]['id'] == 2)
    print("  Product 1 (index 0) should still have id=0:", product_objects[2]['id'] == 0)
    print("  Product 4 (index 3) should still have id=3:", product_objects[3]['id'] == 3)

    ids_preserved = (
        product_objects[0]['id'] == 1 and
        product_objects[1]['id'] == 2 and
        product_objects[2]['id'] == 0 and
        product_objects[3]['id'] == 3
    )

    print("\n" + "=" * 60)
    if all_passed and ids_preserved:
        print("✓ ALL TESTS PASSED")
        print("  - Products sorted correctly by creation time")
        print("  - Original IDs preserved for stable routing")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    return all_passed and ids_preserved


if __name__ == "__main__":
    success = test_product_sorting()
    exit(0 if success else 1)
