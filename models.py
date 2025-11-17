"""
Database models for AI Price Tracker.

Uses SQLAlchemy ORM with SQLite database (the standard for Python web applications).
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pathlib import Path

Base = declarative_base()


class Product(Base):
    """Product model - tracks items to monitor."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False, unique=True)

    # Notification settings
    notify_on_price_drop = Column(Boolean, default=True)
    notify_on_availability = Column(Boolean, default=True)
    track_variants = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Favicon path (cached)
    favicon_path = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    price_history = relationship('PriceHistory', back_populates='product', cascade='all, delete-orphan', order_by='PriceHistory.checked_at.desc()')

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"

    @property
    def latest_price(self):
        """Get the most recent price check."""
        if self.price_history:
            return self.price_history[0]
        return None


class PriceHistory(Base):
    """Price history model - stores price check results."""
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

    # Price data
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    condition = Column(String(100), nullable=True)

    # Availability
    can_add_to_cart = Column(Boolean, default=False)
    in_stock = Column(Boolean, default=False)

    # Metadata
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Raw data (for debugging)
    raw_data = Column(JSON, nullable=True)

    # Relationships
    product = relationship('Product', back_populates='price_history')
    variants = relationship('Variant', back_populates='price_check', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, price=${self.price}, checked_at={self.checked_at})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'price': self.price,
            'original_price': self.original_price,
            'discount': self.discount,
            'condition': self.condition,
            'can_add_to_cart': self.can_add_to_cart,
            'in_stock': self.in_stock,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None,
            'variants': [v.to_dict() for v in self.variants] if self.variants else []
        }


class Variant(Base):
    """Variant model - stores product variants (e.g., different conditions, sizes)."""
    __tablename__ = 'variants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price_history_id = Column(Integer, ForeignKey('price_history.id'), nullable=False)

    # Variant details
    condition = Column(String(100), nullable=True)
    size = Column(String(100), nullable=True)
    color = Column(String(100), nullable=True)
    sku = Column(String(200), nullable=True)

    # Price data
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)

    # Availability
    can_add_to_cart = Column(Boolean, default=False)
    in_stock = Column(Boolean, default=False)

    # Additional metadata (stored as JSON)
    variant_metadata = Column(JSON, nullable=True)

    # Relationships
    price_check = relationship('PriceHistory', back_populates='variants')

    def __repr__(self):
        return f"<Variant(id={self.id}, condition='{self.condition}', price=${self.price})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'condition': self.condition,
            'size': self.size,
            'color': self.color,
            'sku': self.sku,
            'price': self.price,
            'original_price': self.original_price,
            'discount': self.discount,
            'can_add_to_cart': self.can_add_to_cart,
            'in_stock': self.in_stock,
            'metadata': self.variant_metadata
        }


class Notification(Base):
    """Notification model - tracks sent notifications to avoid duplicates."""
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

    # Notification details
    notification_type = Column(String(50), nullable=False)  # 'price_drop', 'availability_change'
    message = Column(Text, nullable=False)

    # Metadata
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', sent_at={self.sent_at})>"


# Database connection and session management
class Database:
    """Database manager with session handling."""

    def __init__(self, db_path='tracker.db'):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        print(f"✓ Database tables created at {self.db_path}")

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    def drop_all_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(self.engine)
        print("⚠ All tables dropped")


# Global database instance
db = Database()


if __name__ == "__main__":
    # Create tables when run directly
    db.create_tables()

    # Test the models
    print("\nTesting models...")
    session = db.get_session()

    # Create a test product
    test_product = Product(
        name="Test MacBook Pro",
        url="https://example.com/test",
        notify_on_price_drop=True,
        notify_on_availability=True,
        track_variants=True
    )

    session.add(test_product)
    session.commit()

    # Add price history
    price_check = PriceHistory(
        product_id=test_product.id,
        price=1299.99,
        original_price=1999.99,
        discount=35.0,
        condition="Fair",
        can_add_to_cart=True,
        in_stock=True
    )

    session.add(price_check)
    session.commit()

    # Query and display
    products = session.query(Product).all()
    print(f"\n✓ Created {len(products)} test product(s)")
    for p in products:
        print(f"  - {p.name}: ${p.latest_price.price if p.latest_price else 'N/A'}")

    # Cleanup
    session.query(Product).delete()
    session.commit()
    session.close()

    print("\n✓ Models test complete")
