from decimal import Decimal
from typing import Dict, List

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import cache
from ..repositories.product_repository import ProductRepository
from ..schemas.cart import (
    CartClearResponse,
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
)

logger = structlog.get_logger()


class CartService:
    """
    Service for cart operations using Redis for storage.
    Cart is stored per session/user in Redis.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)

    def _get_cart_key(self, session_id: str) -> str:
        """Generate Redis key for cart"""
        return f"cart:{session_id}"

    async def _get_cart_data(self, session_id: str) -> Dict:
        """Get cart data from Redis"""
        cart_data = await cache.get(self._get_cart_key(session_id))
        if not cart_data:
            return {}
        return cart_data

    async def _save_cart_data(self, session_id: str, cart_data: Dict):
        """Save cart data to Redis with 7 days TTL"""
        await cache.set(self._get_cart_key(session_id), cart_data, ttl=604800)  # 7 days

    async def get_cart(self, session_id: str) -> CartResponse:
        """
        Get full cart with product details.
        Fetches cart from Redis and enriches with product data from DB.
        """
        cart_data = await self._get_cart_data(session_id)

        if not cart_data:
            logger.info("empty_cart", session_id=session_id)
            return CartResponse(items=[], total_items=0, total_price=Decimal("0.00"))

        # Fetch product details for all items in cart
        items = []
        total_price = Decimal("0.00")
        total_items = 0

        for product_id_str, quantity in cart_data.items():
            product_id = int(product_id_str)
            product = await self.product_repo.get_by_id(product_id)

            if not product or not product.is_active:
                # Product not found or inactive - skip it
                logger.warning("cart_product_not_found", product_id=product_id)
                continue

            subtotal = product.price * quantity
            total_price += subtotal
            total_items += quantity

            items.append(
                CartItemResponse(
                    product_id=product.id,
                    product_name=product.name,
                    product_price=product.price,
                    product_image_url=product.image_url,
                    quantity=quantity,
                    subtotal=subtotal,
                )
            )

        logger.info("cart_retrieved", session_id=session_id, items=len(items))

        return CartResponse(items=items, total_items=total_items, total_price=total_price)

    async def add_item(self, session_id: str, item_data: CartItemCreate) -> CartResponse:
        """
        Add item to cart or update quantity if already exists.
        Validates product existence and stock availability.
        """
        # Check if product exists and is active
        product = await self.product_repo.get_by_id(item_data.product_id)
        if not product or product.is_active == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found",
            )

        # Check stock availability
        if not await self.product_repo.check_stock(item_data.product_id, item_data.quantity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {item_data.product_id}",
            )

        # Get current cart
        cart_data = await self._get_cart_data(session_id)

        # Add or update item
        product_key = str(item_data.product_id)
        if product_key in cart_data:
            # Update quantity
            new_quantity = cart_data[product_key] + item_data.quantity

            # Check stock for new quantity
            if not await self.product_repo.check_stock(item_data.product_id, new_quantity):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {product.stock_quantity}",
                )

            cart_data[product_key] = new_quantity
            logger.info(
                "cart_item_updated",
                product_id=item_data.product_id,
                quantity=new_quantity,
            )
        else:
            cart_data[product_key] = item_data.quantity
            logger.info(
                "cart_item_added",
                product_id=item_data.product_id,
                quantity=item_data.quantity,
            )

        # Save updated cart
        await self._save_cart_data(session_id, cart_data)

        # Return updated cart
        return await self.get_cart(session_id)

    async def update_item(self, session_id: str, product_id: int, item_data: CartItemUpdate) -> CartResponse:
        """
        Update item quantity in cart.
        Set quantity to remove item.
        """
        cart_data = await self._get_cart_data(session_id)
        product_key = str(product_id)

        if product_key not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not in cart",
            )

        # Check stock availability
        if not await self.product_repo.check_stock(product_id, item_data.quantity):
            product = await self.product_repo.get_by_id(product_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.stock_quantity}",
            )

        # Update quantity
        cart_data[product_key] = item_data.quantity
        await self._save_cart_data(session_id, cart_data)

        logger.info(
            "cart_item_quantity_updated",
            product_id=product_id,
            quantity=item_data.quantity,
        )

        return await self.get_cart(session_id)

    async def remove_item(self, session_id: str, product_id: int) -> CartResponse:
        """Remove item from cart"""
        cart_data = await self._get_cart_data(session_id)
        product_key = str(product_id)

        if product_key not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not in cart",
            )

        del cart_data[product_key]
        await self._save_cart_data(session_id, cart_data)

        logger.info("cart_item_removed", product_id=product_id)

        return await self.get_cart(session_id)

    async def clear_cart(self, session_id: str) -> CartClearResponse:
        """Clear all items from cart"""
        cart_data = await self._get_cart_data(session_id)
        items_count = len(cart_data)

        # Delete cart from Redis
        await cache.delete(self._get_cart_key(session_id))

        logger.info("cart_cleared", session_id=session_id, items_removed=items_count)

        return CartClearResponse(message="Cart cleared successfully", items_removed=items_count)
