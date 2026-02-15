from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_empty_cart(client: AsyncClient):
    """Test getting empty cart"""
    response = await client.get("/api/cart")

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 0
    assert data["total_price"] == "0.00"
    assert data["items"] == []

    # Check that session cookie is set
    assert "cart_session_id" in response.cookies


@pytest.mark.asyncio
async def test_add_item_to_cart(client: AsyncClient, test_product):
    """Test adding item to cart"""
    cart_item = {"product_id": test_product.id, "quantity": 2}

    response = await client.post("/api/cart", json=cart_item)

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == test_product.id
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["product_name"] == "Test Product"
    assert data["items"][0]["subtotal"] == "199.98"  # 99.99 * 2


@pytest.mark.asyncio
async def test_add_item_to_cart_invalid_product(client: AsyncClient):
    """Test adding non-existent product to cart"""
    cart_item = {"product_id": 999, "quantity": 1}

    response = await client.post("/api/cart", json=cart_item)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_item_insufficient_stock(client: AsyncClient, test_product):
    """Test adding item with quantity exceeding stock"""
    # test_product has stock_quantity=10
    cart_item = {"product_id": test_product.id, "quantity": 20}  # More than available

    response = await client.post("/api/cart", json=cart_item)

    assert response.status_code == 400
    assert "insufficient stock" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_duplicate_item_updates_quantity(client: AsyncClient, test_product):
    """Test adding same item twice updates quantity"""
    cart_item = {"product_id": test_product.id, "quantity": 2}

    # Add first time
    response1 = await client.post("/api/cart", json=cart_item)
    session_cookie = response1.cookies.get("cart_session_id")

    # Add again with same session
    response2 = await client.post("/api/cart", json=cart_item, cookies={"cart_session_id": session_cookie})

    assert response2.status_code == 200
    data = response2.json()
    assert data["total_items"] == 4  # 2 + 2
    assert len(data["items"]) == 1  # Still one unique product
    assert data["items"][0]["quantity"] == 4


@pytest.mark.asyncio
async def test_update_cart_item_quantity(client: AsyncClient, test_product):
    """Test updating item quantity in cart"""
    # Add item first
    cart_item = {"product_id": test_product.id, "quantity": 2}
    response = await client.post("/api/cart", json=cart_item)
    session_cookie = response.cookies.get("cart_session_id")

    # Update quantity
    update_data = {"quantity": 5}
    response = await client.patch(
        f"/api/cart/{test_product.id}",
        json=update_data,
        cookies={"cart_session_id": session_cookie},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 5
    assert data["items"][0]["quantity"] == 5
    assert data["items"][0]["subtotal"] == "499.95"  # 99.99 * 5


@pytest.mark.asyncio
async def test_update_nonexistent_cart_item(client: AsyncClient):
    """Test updating item not in cart"""
    update_data = {"quantity": 5}
    response = await client.patch("/api/cart/999", json=update_data)

    assert response.status_code == 404
    assert "not in cart" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_remove_item_from_cart(client: AsyncClient, test_product):
    """Test removing item from cart"""
    # Add item first
    cart_item = {"product_id": test_product.id, "quantity": 2}
    response = await client.post("/api/cart", json=cart_item)
    session_cookie = response.cookies.get("cart_session_id")

    # Remove item
    response = await client.delete(f"/api/cart/{test_product.id}", cookies={"cart_session_id": session_cookie})

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_clear_cart(client: AsyncClient, test_product, db_session):
    """Test clearing entire cart"""
    from app.models.product import Product

    # Create another product
    product2 = Product(
        name="Product 2",
        description="Description",
        price=Decimal("49.99"),
        category_id=test_product.category_id,
        stock_quantity=10,
        is_active=1,
    )
    db_session.add(product2)
    await db_session.commit()
    await db_session.refresh(product2)

    # Add both products to cart
    response = await client.post("/api/cart", json={"product_id": test_product.id, "quantity": 2})
    session_cookie = response.cookies.get("cart_session_id")

    await client.post(
        "/api/cart",
        json={"product_id": product2.id, "quantity": 1},
        cookies={"cart_session_id": session_cookie},
    )

    # Clear cart
    response = await client.delete("/api/cart", cookies={"cart_session_id": session_cookie})

    assert response.status_code == 200
    data = response.json()
    assert data["items_removed"] == 2
    assert "cleared" in data["message"].lower()

    # Verify cart is empty
    get_response = await client.get("/api/cart", cookies={"cart_session_id": session_cookie})
    assert get_response.json()["total_items"] == 0


@pytest.mark.asyncio
async def test_cart_with_multiple_products(client: AsyncClient, test_product, db_session):
    """Test cart with multiple different products"""
    from app.models.product import Product

    # Create additional products
    products = []
    for i in range(3):
        product = Product(
            name=f"Product {i}",
            description=f"Description {i}",
            price=Decimal("25.00") + Decimal(str(i * 5)),
            category_id=test_product.category_id,
            stock_quantity=10,
            is_active=1,
        )
        db_session.add(product)
        products.append(product)

    await db_session.commit()
    for p in products:
        await db_session.refresh(p)

    # Add all products to cart
    response = await client.post("/api/cart", json={"product_id": test_product.id, "quantity": 2})
    session_cookie = response.cookies.get("cart_session_id")

    for product in products:
        await client.post(
            "/api/cart",
            json={"product_id": product.id, "quantity": 1},
            cookies={"cart_session_id": session_cookie},
        )

    # Get cart
    response = await client.get("/api/cart", cookies={"cart_session_id": session_cookie})

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 4  # test_product + 3 new products
    assert data["total_items"] == 5  # 2 + 1 + 1 + 1

    # Verify total price calculation
    expected_total = (Decimal("99.99") * 2) + Decimal("25.00") + Decimal("30.00") + Decimal("35.00")
    assert Decimal(data["total_price"]) == expected_total


@pytest.mark.asyncio
async def test_cart_session_persistence(client: AsyncClient, test_product):
    """Test that cart persists across requests with same session"""
    # Add item
    response1 = await client.post("/api/cart", json={"product_id": test_product.id, "quantity": 2})
    session_cookie = response1.cookies.get("cart_session_id")

    # Get cart in new request with same session
    response2 = await client.get("/api/cart", cookies={"cart_session_id": session_cookie})

    assert response2.status_code == 200
    data = response2.json()
    assert data["total_items"] == 2
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_cart_ignores_inactive_products(client: AsyncClient, test_product, db_session):
    """Test that cart filters out inactive products"""
    # Add product to cart
    response = await client.post("/api/cart", json={"product_id": test_product.id, "quantity": 2})
    session_cookie = response.cookies.get("cart_session_id")

    # Deactivate product
    test_product.is_active = 0
    await db_session.commit()

    # Get cart - should be empty
    response = await client.get("/api/cart", cookies={"cart_session_id": session_cookie})

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 0
    assert len(data["items"]) == 0
