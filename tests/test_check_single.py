#!/usr/bin/env python3
"""
Test the check_single_product method directly.
"""

import sys
from price_tracker import PriceTracker

def test_check_product(product_id):
    """Test checking a single product."""
    print(f"Testing check_single_product for product ID: {product_id}\n")
    
    tracker = PriceTracker()
    success = tracker.check_single_product(product_id)
    
    if success:
        print(f"\n✅ Successfully checked product {product_id}")
    else:
        print(f"\n❌ Failed to check product {product_id}")
    
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_check_single.py <product_id>")
        sys.exit(1)
    
    product_id = int(sys.argv[1])
    success = test_check_product(product_id)
    sys.exit(0 if success else 1)
