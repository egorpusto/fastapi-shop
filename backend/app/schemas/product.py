from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base product schema with common fields"""

    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Product price")
    category_id: int = Field(..., gt=0, description="Category ID")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    stock_quantity: int = Field(default=0, ge=0, description="Available stock quantity")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[int] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Schema for paginated product list"""

    items: list[ProductResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    model_config = ConfigDict(from_attributes=True)


class ProductFilter(BaseModel):
    """Schema for filtering products"""

    category_id: Optional[int] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    search: Optional[str] = Field(None, max_length=100, description="Search in name and description")
    is_active: bool = True
    in_stock: Optional[bool] = None  # Filter only products with stock > 0
