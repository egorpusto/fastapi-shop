import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_categories_empty(client: AsyncClient):
    """Test getting categories when database is empty"""
    response = await client.get("/api/categories")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_categories_with_data(client: AsyncClient, test_category):
    """Test getting categories with data"""
    response = await client.get("/api/categories")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Category"
    assert data["items"][0]["slug"] == "test-category"


@pytest.mark.asyncio
async def test_get_category_by_id(client: AsyncClient, test_category):
    """Test getting single category by ID"""
    response = await client.get(f"/api/categories/{test_category.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_category.id
    assert data["name"] == "Test Category"
    assert data["slug"] == "test-category"


@pytest.mark.asyncio
async def test_get_category_by_slug(client: AsyncClient, test_category):
    """Test getting category by slug"""
    response = await client.get("/api/categories/slug/test-category")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_category.id
    assert data["slug"] == "test-category"


@pytest.mark.asyncio
async def test_get_category_not_found(client: AsyncClient):
    """Test getting non-existent category"""
    response = await client.get("/api/categories/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient):
    """Test creating a new category"""
    category_data = {
        "name": "New Category",
        "slug": "new-category",
        "description": "New category description",
    }

    response = await client.post("/api/categories", json=category_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"
    assert data["slug"] == "new-category"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_category_duplicate_slug(client: AsyncClient, test_category):
    """Test creating category with duplicate slug"""
    category_data = {
        "name": "Another Category",
        "slug": "test-category",  # Same slug as test_category
        "description": "Description",
    }

    response = await client.post("/api/categories", json=category_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient, test_category):
    """Test updating a category"""
    update_data = {"name": "Updated Category", "description": "Updated description"}

    response = await client.patch(f"/api/categories/{test_category.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["description"] == "Updated description"
    assert data["slug"] == test_category.slug  # Unchanged


@pytest.mark.asyncio
async def test_delete_category(client: AsyncClient, test_category):
    """Test soft deleting a category"""
    response = await client.delete(f"/api/categories/{test_category.id}")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Verify category is soft deleted
    get_response = await client.get("/api/categories")
    assert get_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_categories_with_product_count(client: AsyncClient, test_category, test_product):
    """Test getting categories with product count"""
    response = await client.get("/api/categories?with_product_count=true")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["product_count"] == 1


@pytest.mark.asyncio
async def test_get_categories_include_inactive(client: AsyncClient, db_session):
    """Test getting inactive categories"""
    from app.models.category import Category

    # Create inactive category
    inactive_cat = Category(name="Inactive Category", slug="inactive", is_active=0)
    db_session.add(inactive_cat)
    await db_session.commit()

    # Without include_inactive
    response = await client.get("/api/categories")
    assert response.json()["total"] == 0

    # With include_inactive
    response = await client.get("/api/categories?include_inactive=true")
    assert response.json()["total"] == 1
