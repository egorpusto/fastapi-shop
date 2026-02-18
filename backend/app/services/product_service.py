from typing import Optional

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import cache
from ..repositories.product_repository import ProductRepository
from ..schemas.product import (
    ProductCreate,
    ProductFilter,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

logger = structlog.get_logger()


class ProductService:
    """Service layer for product business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProductRepository(db)

    async def get_all_products(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[ProductFilter] = None,
    ) -> ProductListResponse:
        """
        Get all products with pagination and caching.
        Cache key includes page, page_size, and filters.
        """
        # Build cache key from filters
        cache_key = f"products:page:{page}:size:{page_size}"
        if filters:
            if filters.category_id:
                cache_key += f":cat:{filters.category_id}"
            if filters.search:
                cache_key += f":search:{filters.search}"
            if filters.min_price:
                cache_key += f":minp:{filters.min_price}"
            if filters.max_price:
                cache_key += f":maxp:{filters.max_price}"

        # Try to get from cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("products_cache_hit", key=cache_key)
            return ProductListResponse.model_validate(cached_data)

        # Calculate pagination
        skip = (page - 1) * page_size

        # Get from database
        products, total = await self.repository.get_all(skip=skip, limit=page_size, filters=filters)

        # Calculate total pages
        pages = (total + page_size - 1) // page_size

        # Build response
        response = ProductListResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

        # Cache response
        await cache.set(cache_key, response.model_dump(), ttl=300)  # 5 minutes
        logger.info("products_cache_miss", key=cache_key, total=total)

        return response

    async def get_product_by_id(self, product_id: int) -> ProductResponse:
        """Get single product by ID with caching"""
        cache_key = f"product:{product_id}"

        # Try cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info("product_cache_hit", product_id=product_id)
            return ProductResponse.model_validate(cached_data)

        # Get from database
        product = await self.repository.get_by_id(product_id)
        if not product:
            logger.warning("product_not_found", product_id=product_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )

        response = ProductResponse.model_validate(product)

        # Cache it
        await cache.set(cache_key, response.model_dump(), ttl=600)  # 10 minutes
        logger.info("product_cache_miss", product_id=product_id)

        return response

    async def get_products_by_category(self, category_id: int, page: int = 1, page_size: int = 20) -> ProductListResponse:
        """Get products by category with pagination"""
        filters = ProductFilter(category_id=category_id, is_active=True)
        return await self.get_all_products(page=page, page_size=page_size, filters=filters)

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create new product and invalidate cache"""
        try:
            product = await self.repository.create(product_data.model_dump())

            # Invalidate products list cache
            await cache.clear_pattern("products:*")

            logger.info("product_created", product_id=product.id, name=product.name)

            return ProductResponse.model_validate(product)
        except Exception as e:
            logger.error("product_creation_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create product: {str(e)}",
            )

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> ProductResponse:
        """Update product and invalidate cache"""
        # Filter out None values
        update_data = {
            k: v for k, v in product_data.model_dump(exclude_unset=True).items()
        }

        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        product = await self.repository.update(product_id, update_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )

        # Invalidate cache
        await cache.delete(f"product:{product_id}")
        await cache.clear_pattern("products:*")
        await cache.clear_pattern("categories:*")

        logger.info("product_updated", product_id=product_id)

        return ProductResponse.model_validate(product)

    async def delete_product(self, product_id: int) -> dict:
        """Soft delete product and invalidate cache"""
        success = await self.repository.delete(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )

        # Invalidate cache
        await cache.delete(f"product:{product_id}")
        await cache.clear_pattern("products:*")
        await cache.clear_pattern("categories:*")

        logger.info("product_deleted", product_id=product_id)

        return {"message": "Product deleted successfully", "product_id": product_id}

    async def check_availability(self, product_id: int, quantity: int) -> bool:
        """Check if product is available in requested quantity"""
        return await self.repository.check_stock(product_id, quantity)
