from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models.category import Category


class CategoryRepository:
    """Repository for category database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, include_inactive: bool = False) -> List[Category]:
        """
        Get all categories.
        By default returns only active categories.
        """
        query = select(Category)

        if not include_inactive:
            query = query.where(Category.is_active == 1)

        query = query.order_by(Category.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_product_count(self, include_inactive: bool = False) -> List[dict]:
        """
        Get all categories with product count.
        Returns list of dicts with category data and product_count.
        """
        query = select(Category).options(selectinload(Category.products))

        if not include_inactive:
            query = query.where(Category.is_active == 1)

        query = query.order_by(Category.name)

        result = await self.db.execute(query)
        categories = result.scalars().unique().all()

        # Build response with product count
        categories_with_count = []
        for category in categories:
            category_dict = category.to_dict()
            # Count only active products
            active_products = [p for p in category.products if p.is_active == 1]
            category_dict["product_count"] = len(active_products)
            categories_with_count.append(category_dict)

        return categories_with_count

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug (for SEO-friendly URLs)"""
        query = select(Category).where(Category.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, category_data: dict) -> Category:
        """Create new category"""
        category = Category(**category_data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category_id: int, category_data: dict) -> Optional[Category]:
        """Update existing category"""
        category = await self.get_by_id(category_id)
        if not category:
            return None

        for key, value in category_data.items():
            if value is not None:
                setattr(category, key, value)

        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: int) -> bool:
        """Soft delete category (set is_active to 0)"""
        category = await self.get_by_id(category_id)
        if not category:
            return False

        category.is_active = 0
        await self.db.commit()
        return True

    async def exists(self, category_id: int) -> bool:
        """Check if category exists and is active"""
        query = select(func.count()).where(Category.id == category_id, Category.is_active == 1)
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0
