#!/usr/bin/env python3
"""
Migration script to add created_at timestamps to existing products.
"""

import json
from datetime import datetime
from pathlib import Path

CONFIG_FILE = "config.json"


def migrate_config():
    """Add created_at timestamps to products that don't have them."""
    print("=" * 60)
    print("Migration: Adding created_at timestamps to products")
    print("=" * 60)

    if not Path(CONFIG_FILE).exists():
        print(f"\n❌ Config file {CONFIG_FILE} not found. Nothing to migrate.")
        return

    # Load config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    products = config.get('products', [])

    if not products:
        print("\n✓ No products found. Nothing to migrate.")
        return

    # Check how many products need migration
    needs_migration = sum(1 for p in products if 'created_at' not in p)

    if needs_migration == 0:
        print(f"\n✓ All {len(products)} products already have timestamps.")
        return

    print(f"\nFound {len(products)} products:")
    print(f"  - {len(products) - needs_migration} with timestamps")
    print(f"  - {needs_migration} without timestamps (will add)")

    # Add timestamps to products that don't have them
    # Use current time, staggered by 1 second for each product to maintain order
    base_time = datetime.now()
    migrated_count = 0

    for i, product in enumerate(products):
        if 'created_at' not in product:
            # Stagger timestamps by index to preserve original order
            # Older products get older timestamps
            timestamp = base_time.replace(
                second=max(0, base_time.second - (len(products) - i))
            ).isoformat()

            product['created_at'] = timestamp
            migrated_count += 1
            print(f"\n  ✓ Added timestamp to: {product.get('name', 'Unknown')}")
            print(f"    Created at: {timestamp}")

    # Save updated config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✓ Migration complete!")
    print(f"  - {migrated_count} products updated")
    print(f"  - Config saved to {CONFIG_FILE}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    migrate_config()
