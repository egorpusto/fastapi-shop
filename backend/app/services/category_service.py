import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import cache
from ..repositories.category_repository import CategoryRepository
from ..schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)

logger = structlog.get_logger()


class CategoryService:
    """Service layer for category business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CategoryRepository(db)

    async def get_all_categories(
        self, include_inactive: bool = False, with_product_count: bool = True
    ) -> CategoryListResponse:
        """
        Get all categories with caching.
        Optionally includes product count for each category.
        """
        cache_key = f"categories:all:inactive:{include_inactive}:count:{with_product_count}"

        # Try cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("categories_cache_hit", key=cache_key)
            return CategoryListResponse.model_validate(cached_data)

        # Get from database
        if with_product_count:
            categories_data = await self.repository.get_with_product_count(include_inactive)
            categories = [CategoryResponse(**cat) for cat in categories_data]
        else:
            categories_db = await self.repository.get_all(include_inactive)
            categories = [CategoryResponse.model_validate(cat) for cat in categories_db]

        response = CategoryListResponse(items=categories, total=len(categories))

        # Cache response
        await cache.set(cache_key, response.model_dump(), ttl=600)  # 10 minutes
        logger.info("categories_cache_miss", key=cache_key, total=len(categories))

        return response

    async def get_category_by_id(self, category_id: int) -> CategoryResponse:
        """Get single category by ID with caching"""
        cache_key = f"category:{category_id}"

        # Try cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("category_cache_hit", category_id=category_id)
            return CategoryResponse.model_validate(cached_data)

        # Get from database
        category = await self.repository.get_by_id(category_id)
        if not category:
            logger.warning("category_not_found", category_id=category_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        response = CategoryResponse.model_validate(category)

        # Cache it
        await cache.set(cache_key, response.model_dump(), ttl=600)
        logger.info("category_cache_miss", category_id=category_id)

        return response

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        """Get category by slug (SEO-friendly)"""
        cache_key = f"category:slug:{slug}"

        # Try cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("category_slug_cache_hit", slug=slug)
            return CategoryResponse.model_validate(cached_data)

        # Get from database
        category = await self.repository.get_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with slug '{slug}' not found",
            )

        response = CategoryResponse.model_validate(category)
        await cache.set(cache_key, response.model_dump(), ttl=600)

        return response

    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """Create new category and invalidate cache"""
        # Check if slug already exists
        existing = await self.repository.get_by_slug(category_data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with slug '{category_data.slug}' already exists",
            )

        try:
            category = await self.repository.create(category_data.model_dump())

            # Invalidate cache
            await cache.clear_pattern("categories:*")

            logger.info("category_created", category_id=category.id, name=category.name)

            return CategoryResponse.model_validate(category)
        except Exception as e:
            logger.error("category_creation_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create category: {str(e)}",
            )

    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> CategoryResponse:
        """Update category and invalidate cache"""
        # Filter out None values
        update_data = {
            k: v for k, v in category_data.model_dump(exclude_unset=True).items()
        }

        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        # If updating slug, check uniqueness
        if "slug" in update_data:
            existing = await self.repository.get_by_slug(update_data["slug"])
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with slug '{update_data['slug']}' already exists",
                )

        category = await self.repository.update(category_id, update_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        # Invalidate cache
        await cache.delete(f"category:{category_id}")
        await cache.clear_pattern("categories:*")
        await cache.clear_pattern("products:*")  # Products cache depends on categories

        logger.info("category_updated", category_id=category_id)

        return CategoryResponse.model_validate(category)

    async def delete_category(self, category_id: int) -> dict:
        """Soft delete category and invalidate cache"""
        success = await self.repository.delete(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        # Invalidate cache
        await cache.delete(f"category:{category_id}")
        await cache.clear_pattern("categories:*")
        await cache.clear_pattern("products:*")

        logger.info("category_deleted", category_id=category_id)

        return {"message": "Category deleted successfully", "category_id": category_id}
