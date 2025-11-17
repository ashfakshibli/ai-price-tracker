#!/usr/bin/env python3
"""
Migration script to move from JSON files to SQLite database.

This script:
1. Reads config.json for products
2. Reads data/*.json for price history
3. Creates SQLite database with proper models
4. Migrates all data to the database
"""

import json
from pathlib import Path
from datetime import datetime
import hashlib

from models import db, Product, PriceHistory, Variant


def parse_datetime(dt_string):
    """Parse datetime string in various formats."""
    if not dt_string:
        return datetime.utcnow()

    # Try ISO format
    try:
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    except:
        pass

    # Try other common formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_string, fmt)
        except:
            continue

    # Default to now if parsing fails
    return datetime.utcnow()


def migrate_products():
    """Migrate products from config.json to database."""
    print("=" * 70)
    print("Migrating from JSON to SQLite Database")
    print("=" * 70)

    # Create database tables
    print("\n[1/4] Creating database tables...")
    db.create_tables()

    # Load config
    config_file = Path("config.json")
    if not config_file.exists():
        print("  ⚠ config.json not found. Starting with empty database.")
        return

    with open(config_file, 'r') as f:
        config = json.load(f)

    products_data = config.get('products', [])
    print(f"  ✓ Found {len(products_data)} products in config.json")

    if not products_data:
        print("  ✓ No products to migrate")
        return

    # Start migration
    print("\n[2/4] Migrating products...")
    session = db.get_session()

    migrated_products = []

    for product_data in products_data:
        # Create Product
        product = Product(
            name=product_data['name'],
            url=product_data['url'],
            notify_on_price_drop=product_data.get('notify_on_price_drop', True),
            notify_on_availability=product_data.get('notify_on_availability', True),
            track_variants=product_data.get('track_variants', True),
            created_at=parse_datetime(product_data.get('created_at')),
            is_active=True
        )

        session.add(product)
        session.flush()  # Get the ID without committing

        migrated_products.append({
            'product': product,
            'hash_id': hashlib.md5(product.url.encode()).hexdigest()[:12]
        })

        print(f"  ✓ Migrated product: {product.name} (ID: {product.id})")

    session.commit()

    # Migrate price history
    print("\n[3/4] Migrating price history...")
    data_dir = Path("data")

    if not data_dir.exists():
        print("  ⚠ data/ directory not found. Skipping price history.")
    else:
        for item in migrated_products:
            product = item['product']
            hash_id = item['hash_id']
            history_file = data_dir / f"{hash_id}.json"

            if not history_file.exists():
                print(f"  - No history for {product.name}")
                continue

            with open(history_file, 'r') as f:
                history_data = json.load(f)

            # Migrate current price
            current = history_data.get('current')
            if current:
                price_check = PriceHistory(
                    product_id=product.id,
                    price=current['price'],
                    original_price=current.get('original_price'),
                    discount=current.get('discount'),
                    condition=current.get('condition'),
                    can_add_to_cart=current.get('can_add_to_cart', False),
                    in_stock=current.get('in_stock', False),
                    checked_at=parse_datetime(current.get('checked_at')),
                    raw_data=current
                )
                session.add(price_check)
                session.flush()

                # Add variants
                variants = current.get('variants', [])
                for variant_data in variants:
                    variant = Variant(
                        price_history_id=price_check.id,
                        condition=variant_data.get('condition'),
                        size=variant_data.get('size'),
                        color=variant_data.get('color'),
                        sku=variant_data.get('sku'),
                        price=variant_data.get('price', 0),
                        original_price=variant_data.get('original_price'),
                        discount=variant_data.get('discount'),
                        can_add_to_cart=variant_data.get('can_add_to_cart', False),
                        in_stock=variant_data.get('in_stock', False),
                        variant_metadata=variant_data
                    )
                    session.add(variant)

            # Migrate historical checks
            history = history_data.get('history', [])
            for hist in history:
                price_check = PriceHistory(
                    product_id=product.id,
                    price=hist['price'],
                    original_price=hist.get('original_price'),
                    discount=hist.get('discount'),
                    condition=hist.get('condition'),
                    can_add_to_cart=hist.get('can_add_to_cart', False),
                    in_stock=hist.get('in_stock', False),
                    checked_at=parse_datetime(hist.get('checked_at')),
                    raw_data=hist
                )
                session.add(price_check)

            session.commit()
            print(f"  ✓ Migrated {len(history) + (1 if current else 0)} price checks for {product.name}")

    # Summary
    print("\n[4/4] Migration Summary")
    print("=" * 70)

    total_products = session.query(Product).count()
    total_history = session.query(PriceHistory).count()
    total_variants = session.query(Variant).count()

    print(f"  Products:      {total_products}")
    print(f"  Price Checks:  {total_history}")
    print(f"  Variants:      {total_variants}")
    print(f"\n  Database:      tracker.db")

    session.close()

    print("\n" + "=" * 70)
    print("✓ Migration complete!")
    print("=" * 70)

    # Backup recommendation
    print("\nRecommendation:")
    print("  • Keep config.json and data/ as backup")
    print("  • The app will now use tracker.db for all operations")
    print("  • You can delete JSON files after verifying everything works")


if __name__ == "__main__":
    migrate_products()
