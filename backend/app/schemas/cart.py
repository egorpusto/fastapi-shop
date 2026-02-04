from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class CartItemBase(BaseModel):
    """Base cart item schema"""

    product_id: int = Field(..., gt=0, description="Product ID")
    quantity: int = Field(..., gt=0, le=100, description="Quantity (max 100)")


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart"""

    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""

    quantity: int = Field(..., gt=0, le=100, description="New quantity")


class CartItemResponse(BaseModel):
    """Schema for cart item in response"""

    product_id: int
    product_name: str
    product_price: Decimal
    product_image_url: Optional[str] = None
    quantity: int
    subtotal: Decimal = Field(..., description="Price * Quantity")

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """Schema for full cart response"""

    items: List[CartItemResponse]
    total_items: int = Field(..., description="Total number of items in cart")
    total_price: Decimal = Field(..., description="Total cart price")

    model_config = ConfigDict(from_attributes=True)

class CartClearResponse(BaseModel):
    """Schema for cart clear response"""
    message: str
    items_removed: int