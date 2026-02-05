from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from ..models.product import Product
from ..schemas.product import ProductFilter
from decimal import Decimal


class ProductRepository:
    """Repository for product database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self, skip: int = 0, limit: int = 20, filters: Optional[ProductFilter] = None
    ) -> tuple[List[Product], int]:
        """
        Get all products with pagination and filters.
        Returns tuple of (products, total_count).
        """
        # Build base query
        query = select(Product).options(joinedload(Product.category))

        # Apply filters
        if filters:
            if filters.category_id:
                query = query.where(Product.category_id == filters.category_id)

            if filters.min_price is not None:
                query = query.where(Product.price >= filters.min_price)

            if filters.max_price is not None:
                query = query.where(Product.price <= filters.max_price)

            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term),
                    )
                )

            if filters.is_active is not None:
                query = query.where(Product.is_active == (1 if filters.is_active else 0))

            if filters.in_stock:
                query = query.where(Product.stock_quantity > 0)
        else:
            # Default: show only active products
            query = query.where(Product.is_active == 1)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Product.created_at.desc()).offset(skip).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        products = result.scalars().unique().all()

        return list(products), total

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID with category relationship"""
        query = select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_category(self, category_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Product], int]:
        """Get products by category with pagination"""
        filters = ProductFilter(category_id=category_id, is_active=True)
        return await self.get_all(skip=skip, limit=limit, filters=filters)

    async def create(self, product_data: dict) -> Product:
        """Create new product"""
        product = Product(**product_data)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Update existing product"""
        product = await self.get_by_id(product_id)
        if not product:
            return None

        for key, value in product_data.items():
            if value is not None:
                setattr(product, key, value)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product_id: int) -> bool:
        """Soft delete product (set is_active to 0)"""
        product = await self.get_by_id(product_id)
        if not product:
            return False

        product.is_active = 0
        await self.db.commit()
        return True

    async def check_stock(self, product_id: int, quantity: int) -> bool:
        """Check if product has enough stock"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        return product.stock_quantity >= quantity

    async def decrease_stock(self, product_id: int, quantity: int) -> bool:
        """Decrease product stock (for orders)"""
        product = await self.get_by_id(product_id)
        if not product or product.stock_quantity < quantity:
            return False

        product.stock_quantity -= quantity
        await self.db.commit()
        return True
