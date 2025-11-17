#!/usr/bin/env python3
"""
Test script to verify initial price check when adding a product.
"""

from models import db, Product, PriceHistory

def test_initial_check():
    """Test that products get an initial price check."""
    session = db.get_session()
    
    try:
        # Get all products
        products = session.query(Product).filter_by(is_active=True).all()
        
        print(f"\n{'='*60}")
        print(f"Testing Initial Price Check")
        print(f"{'='*60}\n")
        
        for product in products:
            print(f"Product: {product.name}")
            print(f"  ID: {product.id}")
            print(f"  URL: {product.url}")
            print(f"  Created: {product.created_at}")
            
            # Count price history
            history_count = len(product.price_history)
            print(f"  Price Checks: {history_count}")
            
            if history_count > 0:
                latest = product.latest_price
                print(f"  Latest Check:")
                print(f"    Price: ${latest.price}")
                print(f"    In Stock: {latest.in_stock}")
                print(f"    Can Add to Cart: {latest.can_add_to_cart}")
                print(f"    Checked At: {latest.checked_at}")
                
                if latest.variants:
                    print(f"    Variants: {len(latest.variants)}")
                    for variant in latest.variants:
                        available = 'Available' if variant.can_add_to_cart else 'Unavailable'
                        print(f"      - {variant.condition}: ${variant.price} ({available})")
            else:
                print(f"  ⚠️  NO PRICE CHECKS YET!")
            
            print()
        
        print(f"{'='*60}\n")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_initial_check()
