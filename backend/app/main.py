from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .cache import cache
from .config import settings
from .database import init_db
from .routes import cart_router, categories_router, products_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    logger.info("application_startup", app_name=settings.app_name)

    # Initialize database
    await init_db()
    logger.info("database_initialized")

    # Connect to Redis
    await cache.connect()
    logger.info("redis_connected", redis_url=settings.redis_url.split("@")[1])

    yield

    # Shutdown
    logger.info("application_shutdown")
    await cache.disconnect()
    logger.info("redis_disconnected")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# Include routers
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(cart_router)


@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "Welcome to FastAPI Shop API",
        "version": "2.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Checks Redis connection status.
    """
    redis_status = "connected" if cache.redis_client else "disconnected"

    return {
        "status": "ok",
        "redis": redis_status,
        "debug": settings.debug,
    }
