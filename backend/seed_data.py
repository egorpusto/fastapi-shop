import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker, init_db
from app.models.category import Category
from app.models.product import Product
from decimal import Decimal


async def seed_categories(db: AsyncSession):
    """Seed initial categories"""
    categories_data = [
        {
            "name": "Electronics",
            "slug": "electronics",
            "description": "Electronic devices and gadgets",
            "is_active": 1,
        },
        {
            "name": "Clothing",
            "slug": "clothing",
            "description": "Fashion and apparel",
            "is_active": 1,
        },
        {
            "name": "Books",
            "slug": "books",
            "description": "Books and educational materials",
            "is_active": 1,
        },
        {
            "name": "Home & Garden",
            "slug": "home-garden",
            "description": "Home improvement and garden supplies",
            "is_active": 1,
        },
        {
            "name": "Sports",
            "slug": "sports",
            "description": "Sports equipment and fitness gear",
            "is_active": 1,
        },
    ]

    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)

    await db.commit()
    print(f"✓ Created {len(categories_data)} categories")


async def seed_products(db: AsyncSession):
    """Seed initial products"""
    products_data = [
        # Electronics
        {
            "name": "Wireless Headphones",
            "description": "High-quality noise-cancelling wireless headphones",
            "price": Decimal("149.99"),
            "category_id": 1,
            "stock_quantity": 50,
            "is_active": 1,
            "image_url": "/static/images/headphones.jpg",
        },
        {
            "name": "Smart Watch",
            "description": "Fitness tracking smart watch with heart rate monitor",
            "price": Decimal("299.99"),
            "category_id": 1,
            "stock_quantity": 30,
            "is_active": 1,
            "image_url": "/static/images/smartwatch.jpg",
        },
        {
            "name": "Laptop Stand",
            "description": "Ergonomic adjustable laptop stand",
            "price": Decimal("49.99"),
            "category_id": 1,
            "stock_quantity": 100,
            "is_active": 1,
            "image_url": "/static/images/laptop-stand.jpg",
        },
        # Clothing
        {
            "name": "Cotton T-Shirt",
            "description": "Comfortable 100% cotton t-shirt",
            "price": Decimal("19.99"),
            "category_id": 2,
            "stock_quantity": 200,
            "is_active": 1,
            "image_url": "/static/images/tshirt.jpg",
        },
        {
            "name": "Denim Jeans",
            "description": "Classic fit denim jeans",
            "price": Decimal("59.99"),
            "category_id": 2,
            "stock_quantity": 150,
            "is_active": 1,
            "image_url": "/static/images/jeans.jpg",
        },
        # Books
        {
            "name": "Python Programming Guide",
            "description": "Comprehensive guide to Python programming",
            "price": Decimal("39.99"),
            "category_id": 3,
            "stock_quantity": 75,
            "is_active": 1,
            "image_url": "/static/images/python-book.jpg",
        },
        {
            "name": "Web Development Basics",
            "description": "Learn HTML, CSS, and JavaScript",
            "price": Decimal("44.99"),
            "category_id": 3,
            "stock_quantity": 60,
            "is_active": 1,
            "image_url": "/static/images/webdev-book.jpg",
        },
        # Home & Garden
        {
            "name": "Plant Pot Set",
            "description": "Set of 5 ceramic plant pots",
            "price": Decimal("29.99"),
            "category_id": 4,
            "stock_quantity": 80,
            "is_active": 1,
            "image_url": "/static/images/plant-pots.jpg",
        },
        {
            "name": "LED Desk Lamp",
            "description": "Adjustable LED desk lamp with USB charging",
            "price": Decimal("34.99"),
            "category_id": 4,
            "stock_quantity": 90,
            "is_active": 1,
            "image_url": "/static/images/desk-lamp.jpg",
        },
        # Sports
        {
            "name": "Yoga Mat",
            "description": "Non-slip premium yoga mat",
            "price": Decimal("24.99"),
            "category_id": 5,
            "stock_quantity": 120,
            "is_active": 1,
            "image_url": "/static/images/yoga-mat.jpg",
        },
        {
            "name": "Resistance Bands Set",
            "description": "Set of 5 resistance bands for workout",
            "price": Decimal("19.99"),
            "category_id": 5,
            "stock_quantity": 110,
            "is_active": 1,
            "image_url": "/static/images/resistance-bands.jpg",
        },
    ]

    for prod_data in products_data:
        product = Product(**prod_data)
        db.add(product)

    await db.commit()
    print(f"✓ Created {len(products_data)} products")


async def main():
    """Main seeding function"""
    print("Starting database seeding...")

    # Initialize database
    await init_db()
    print("✓ Database initialized")

    # Create session
    async with async_session_maker() as db:
        # Seed data
        await seed_categories(db)
        await seed_products(db)

    print("✓ Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
