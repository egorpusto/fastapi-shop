import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.cache import cache
from app.config import settings
from app.database import Base, get_db
from app.main import app

# Test database URL (use separate test database)
# Inside Docker use 'postgres' as the host, locally - 'localhost'
DB_HOST = os.getenv("DB_HOST", "postgres")
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://fashop_user:fashop_password@{DB_HOST}:5432/fashop_test_db"
)

# Test Redis URL
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
TEST_REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:6379/1")

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

# Create test session maker
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a clean database session for each test.
    Rolls back changes after test completes.
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with test_async_session_maker() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test client with overridden database dependency.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_category(db_session: AsyncSession):
    """Create a test category"""
    from app.models.category import Category

    category = Category(
        name="Test Category",
        slug="test-category",
        description="Test category description",
        is_active=True,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
async def test_product(db_session: AsyncSession, test_category):
    """Create a test product"""
    from decimal import Decimal

    from app.models.product import Product

    product = Product(
        name="Test Product",
        description="Test product description",
        price=Decimal("99.99"),
        category_id=test_category.id,
        stock_quantity=10,
        is_active=True,
        image_url="/static/images/test.jpg",
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest.fixture(scope="function", autouse=True)
async def clear_redis_cache():
    """Clear Redis cache before each test using test database"""
    from app.cache import cache
    from app.config import settings

    original_url = settings.redis_url

    import redis.asyncio as redis

    test_redis = await redis.from_url(TEST_REDIS_URL, encoding="utf-8", decode_responses=True)
    cache.redis_client = test_redis

    await test_redis.flushdb()
    yield
    await test_redis.flushdb()
    await test_redis.close()
