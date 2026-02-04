import pytest
from httpx import AsyncClient
from decimal import Decimal


@pytest.mark.asyncio
async def test_get_products_empty(client: AsyncClient):
    """Test getting products when database is empty"""
    response = await client.get("/api/products")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_products_with_data(client: AsyncClient, test_product):
    """Test getting products with data"""
    response = await client.get("/api/products")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Product"
    assert data["items"][0]["price"] == "99.99"


@pytest.mark.asyncio
async def test_get_product_by_id(client: AsyncClient, test_product):
    """Test getting single product by ID"""
    response = await client.get(f"/api/products/{test_product.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product.id
    assert data["name"] == "Test Product"
    assert data["price"] == "99.99"
    assert data["stock_quantity"] == 10


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    """Test getting non-existent product"""
    response = await client.get("/api/products/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, test_category):
    """Test creating a new product"""
    product_data = {
        "name": "New Product",
        "description": "New product description",
        "price": "149.99",
        "category_id": test_category.id,
        "stock_quantity": 20,
    }

    response = await client.post("/api/products", json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"
    assert data["price"] == "149.99"
    assert data["stock_quantity"] == 20
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_product_invalid_category(client: AsyncClient):
    """Test creating product with invalid category"""
    product_data = {
        "name": "New Product",
        "description": "Description",
        "price": "99.99",
        "category_id": 999,  # Non-existent category
        "stock_quantity": 10,
    }

    response = await client.post("/api/products", json=product_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, test_product):
    """Test updating a product"""
    update_data = {"name": "Updated Product", "price": "199.99"}

    response = await client.patch(f"/api/products/{test_product.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["price"] == "199.99"
    assert data["description"] == test_product.description  # Unchanged


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient, test_product):
    """Test soft deleting a product"""
    response = await client.delete(f"/api/products/{test_product.id}")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Verify product is soft deleted (not shown in active list)
    get_response = await client.get("/api/products")
    assert get_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_filter_products_by_category(
    client: AsyncClient, test_product, test_category
):
    """Test filtering products by category"""
    response = await client.get(f"/api/products?category_id={test_category.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category_id"] == test_category.id


@pytest.mark.asyncio
async def test_filter_products_by_price_range(client: AsyncClient, test_product):
    """Test filtering products by price range"""
    # Product price is 99.99
    response = await client.get("/api/products?min_price=50&max_price=150")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    # Out of range
    response = await client.get("/api/products?min_price=200&max_price=300")
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_search_products(client: AsyncClient, test_product):
    """Test searching products by name/description"""
    response = await client.get("/api/products?search=Test")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    # Search with no results
    response = await client.get("/api/products?search=NonExistent")
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, db_session, test_category):
    """Test product pagination"""
    from app.models.product import Product

    # Create 25 products
    for i in range(25):
        product = Product(
            name=f"Product {i}",
            description=f"Description {i}",
            price=Decimal("10.00") + Decimal(str(i)),
            category_id=test_category.id,
            stock_quantity=10,
            is_active=1,
        )
        db_session.add(product)
    await db_session.commit()

    # Get first page (default page_size=20)
    response = await client.get("/api/products?page=1&page_size=20")
    data = response.json()
    assert data["total"] == 25
    assert len(data["items"]) == 20
    assert data["page"] == 1
    assert data["pages"] == 2

    # Get second page
    response = await client.get("/api/products?page=2&page_size=20")
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_check_product_availability(client: AsyncClient, test_product):
    """Test checking product stock availability"""
    # Available quantity
    response = await client.get(
        f"/api/products/{test_product.id}/availability?quantity=5"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert data["quantity"] == 5

    # Unavailable quantity (stock is 10)
    response = await client.get(
        f"/api/products/{test_product.id}/availability?quantity=20"
    )
    data = response.json()
    assert data["available"] is False
