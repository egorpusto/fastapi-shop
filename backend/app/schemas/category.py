from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    product_count: Optional[int] = Field(None, description="Number of products in category")

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Schema for category list (with optional pagination)"""

    items: list[CategoryResponse]
    total: int = Field(..., description="Total number of categories")

    model_config = ConfigDict(from_attributes=True)
