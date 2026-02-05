from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.product import (
    ProductCreate,
    ProductFilter,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from ..services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    search: Optional[str] = Query(None, max_length=100, description="Search in name/description"),
    in_stock: Optional[bool] = Query(None, description="Show only in-stock products"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all products with pagination and filtering.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **category_id**: Filter by category
    - **min_price/max_price**: Price range filter
    - **search**: Search in product name and description
    - **in_stock**: Show only products with stock > 0
    """
    service = ProductService(db)

    # Build filters
    filters = ProductFilter(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        search=search,
        is_active=True,
        in_stock=in_stock,
    )

    return await service.get_all_products(page=page, page_size=page_size, filters=filters)


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get single product by ID.

    Returns 404 if product not found.
    """
    service = ProductService(db)
    return await service.get_product_by_id(product_id)


@router.get(
    "/category/{category_id}",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all products in a specific category with pagination.
    """
    service = ProductService(db)
    return await service.get_products_by_category(category_id=category_id, page=page, page_size=page_size)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new product.

    Requires all mandatory fields:
    - name
    - price
    - category_id
    """
    service = ProductService(db)
    return await service.create_product(product_data)


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product_data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update existing product.

    All fields are optional - only provided fields will be updated.
    Returns 404 if product not found.
    """
    service = ProductService(db)
    return await service.update_product(product_id, product_data)


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Soft delete a product (sets is_active to False).

    Product data is preserved in database.
    Returns 404 if product not found.
    """
    service = ProductService(db)
    return await service.delete_product(product_id)


@router.get("/{product_id}/availability", status_code=status.HTTP_200_OK)
async def check_product_availability(
    product_id: int,
    quantity: int = Query(..., ge=1, description="Requested quantity"),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if product is available in requested quantity.

    Useful before adding to cart or placing order.
    """
    service = ProductService(db)
    available = await service.check_availability(product_id, quantity)

    return {"product_id": product_id, "quantity": quantity, "available": available}
