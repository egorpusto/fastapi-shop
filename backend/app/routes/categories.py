from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from ..services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=CategoryListResponse, status_code=status.HTTP_200_OK)
async def get_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    with_product_count: bool = Query(True, description="Include product count"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all categories.

    - **include_inactive**: Show inactive categories (default: False)
    - **with_product_count**: Include number of products in each category (default: True)
    """
    service = CategoryService(db)
    return await service.get_all_categories(include_inactive=include_inactive, with_product_count=with_product_count)

@router.get("/slug/{slug}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Get category by slug (SEO-friendly URL).

    Example: /api/categories/slug/electronics
    Returns 404 if category not found.
    """
    service = CategoryService(db)
    return await service.get_category_by_slug(slug)


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get single category by ID.

    Returns 404 if category not found.
    """
    service = CategoryService(db)
    return await service.get_category_by_id(category_id)



@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new category.

    Requires:
    - **name**: Category name (unique)
    - **slug**: URL-friendly slug (unique)

    Returns 400 if slug already exists.
    """
    service = CategoryService(db)
    return await service.create_category(category_data)


@router.patch("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category_data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update existing category.

    All fields are optional - only provided fields will be updated.
    Returns 404 if category not found.
    Returns 400 if slug already exists for another category.
    """
    service = CategoryService(db)
    return await service.update_category(category_id, category_data)


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Soft delete a category (sets is_active to False).

    Associated products remain in database but category becomes hidden.
    Returns 404 if category not found.
    """
    service = CategoryService(db)
    return await service.delete_category(category_id)
