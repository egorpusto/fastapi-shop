import uuid
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.cart import (
    CartClearResponse,
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)
from ..services.cart_service import CartService

router = APIRouter(prefix="/api/cart", tags=["cart"])


def get_session_id(session_id: Optional[str] = Cookie(None, alias="cart_session_id")) -> str:
    """
    Get or create session ID from cookie.
    Used to identify user's cart in Redis.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.get("", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def get_cart(
    response: Response,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current cart contents.

    Creates a session cookie if it doesn't exist.
    Returns cart with product details and calculated totals.
    """
    # Set cookie for session tracking
    response.set_cookie(
        key="cart_session_id",
        value=session_id,
        max_age=604800,  # 7 days
        httponly=True,
        samesite="lax",
    )

    service = CartService(db)
    return await service.get_cart(session_id)


@router.post("", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def add_to_cart(
    item_data: CartItemCreate,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Add item to cart or update quantity if already exists.

    Validates:
    - Product exists and is active
    - Sufficient stock available

    Returns updated cart.
    """
    # Set cookie
    response.set_cookie(
        key="cart_session_id",
        value=session_id,
        max_age=604800,
        httponly=True,
        samesite="lax",
    )

    service = CartService(db)
    return await service.add_item(session_id, item_data)


@router.patch("/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def update_cart_item(
    product_id: int,
    item_data: CartItemUpdate,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Update quantity of item in cart.

    Returns 404 if product not in cart.
    Returns 400 if insufficient stock.
    """
    service = CartService(db)
    return await service.update_item(session_id, product_id, item_data)


@router.delete("/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def remove_from_cart(
    product_id: int,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove item from cart.

    Returns 404 if product not in cart.
    Returns updated cart after removal.
    """
    service = CartService(db)
    return await service.remove_item(session_id, product_id)


@router.delete("", response_model=CartClearResponse, status_code=status.HTTP_200_OK)
async def clear_cart(session_id: str = Depends(get_session_id), db: AsyncSession = Depends(get_db)):
    """
    Clear all items from cart.

    Returns number of items removed.
    """
    service = CartService(db)
    return await service.clear_cart(session_id)
