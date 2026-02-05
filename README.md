# 🛒 FastAPI Shop - Modern E-commerce API

A production-ready e-commerce REST API built with FastAPI, PostgreSQL, Redis, and Docker. This project started as a learning exercise from a YouTube tutorial and was significantly enhanced with modern best practices, async architecture, caching, comprehensive testing, and more.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7-red.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![CI](https://github.com/egorpusto/fastapi-shop/workflows/CI/badge.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/Coverage-70%25+-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

## 🎯 Project Overview

This project demonstrates a full-stack e-commerce application with a focus on backend architecture and best practices. The API provides complete functionality for managing products, categories, and shopping carts with advanced features like caching, pagination, filtering, and real-time stock management.

### Original vs Enhanced

**Original Tutorial Features:**
- Basic FastAPI application with SQLite
- Simple CRUD operations for products and categories
- Synchronous database operations
- Basic Vue.js frontend
- Docker deployment with Nginx

**My Enhancements:**
- ✨ **Async Architecture** - Full async/await implementation for better performance
- 🐘 **PostgreSQL** - Production-ready database with connection pooling
- 🚀 **Redis Caching** - Smart caching strategy with automatic invalidation
- 📊 **Alembic Migrations** - Database version control and migrations
- 🧪 **Comprehensive Testing** - 70%+ test coverage with pytest
- 📝 **Structured Logging** - JSON-based logging with structlog
- 🔍 **Advanced Filtering** - Search, price range, category filters with pagination
- 📦 **Stock Management** - Real-time inventory tracking and validation
- 🎨 **Clean Architecture** - Separation of concerns (routes → services → repositories)
- 🔐 **Session Management** - Cookie-based cart persistence
- 📈 **Performance Optimization** - Query optimization with eager loading, composite indexes
- 🐳 **Production-Ready Docker** - Multi-stage builds, health checks
- 📚 **API Documentation** - Auto-generated Swagger/ReDoc documentation

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.128.0 - Modern, fast web framework
- **SQLAlchemy** 2.0 - Async ORM with advanced features
- **Pydantic** 2.0 - Data validation and settings management
- **PostgreSQL** 16 - Primary database
- **Redis** 7 - Caching and session storage
- **Alembic** - Database migrations
- **Structlog** - Structured logging

### Testing
- **Pytest** - Testing framework
- **Pytest-asyncio** - Async test support
- **HTTPX** - Async HTTP client for testing
- **Pytest-cov** - Code coverage reporting

### DevOps
- **Docker** & **Docker Compose** - Containerization
- **Nginx** - Reverse proxy
- **Certbot** - SSL/TLS certificates

### Frontend
- **Vue.js** 3 - Progressive JavaScript framework
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Vite** - Fast build tool

## 📋 Features

### Products Management
- ✅ Create, read, update, delete products (CRUD)
- ✅ Advanced filtering (category, price range, search)
- ✅ Pagination with customizable page size
- ✅ Stock quantity tracking
- ✅ Soft delete (products remain in database)
- ✅ Image URL support
- ✅ Redis caching with TTL

### Categories Management
- ✅ Full CRUD operations
- ✅ SEO-friendly slugs
- ✅ Product count per category
- ✅ Soft delete support
- ✅ Unique slug validation

### Shopping Cart
- ✅ Session-based cart (cookie authentication)
- ✅ Add/update/remove items
- ✅ Real-time stock validation
- ✅ Automatic price calculation
- ✅ Redis storage with 7-day TTL
- ✅ Filters out inactive products

### Additional Features
- ✅ Health check endpoint
- ✅ Auto-generated API documentation (Swagger/ReDoc)
- ✅ CORS configuration
- ✅ Static file serving
- ✅ Comprehensive error handling
- ✅ Request/response logging

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment.

### Automated Checks

Every push and pull request triggers:

✅ **Code Quality**
- Linting with flake8
- Code formatting check with black
- Import sorting with isort

✅ **Testing**
- Full test suite with pytest
- PostgreSQL and Redis services
- Coverage report (minimum 70%)

✅ **Security**
- Dependency vulnerability scanning with pip-audit
- Safety checks for known security issues

✅ **Docker**
- Backend image build validation
- Frontend image build validation
- docker-compose configuration test

### Workflow Status

![CI Workflow](https://github.com/egorpusto/fastapi-shop/workflows/CI/badge.svg)

All checks must pass before merging to main branch.

### Running Checks Locally
```bash
# Install dev dependencies
cd backend
pip install flake8 black isort pip-audit safety

# Run linting
flake8 app

# Check formatting
black --check app

# Check imports
isort --check-only app

# Run tests
pytest

# Security scan
pip-audit
```

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/egorpusto/fastapi-shop.git
cd fastapi-shop
```

2. **Create environment file**
```bash
cp backend/.env.example backend/.env
# Edit .env with your settings if needed
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Seed the database** (optional)
```bash
docker-compose exec backend python seed_data.py
```

6. **Access the application**
- API Documentation: http://localhost:8000/api/docs
- API Base URL: http://localhost:8000
- Frontend: http://localhost:3000

### Local Development Setup

1. **Backend setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start PostgreSQL and Redis (via Docker)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Seed database
python seed_data.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Testing

### Run all tests
```bash
cd backend
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_products.py -v
```

### View coverage report
```bash
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key Endpoints

#### Products
```
GET    /api/products              - List products (with pagination & filters)
GET    /api/products/{id}         - Get product details
POST   /api/products              - Create product
PATCH  /api/products/{id}         - Update product
DELETE /api/products/{id}         - Delete product (soft)
GET    /api/products/{id}/availability - Check stock
```

#### Categories
```
GET    /api/categories            - List categories
GET    /api/categories/{id}       - Get category details
GET    /api/categories/slug/{slug} - Get category by slug
POST   /api/categories            - Create category
PATCH  /api/categories/{id}       - Update category
DELETE /api/categories/{id}       - Delete category (soft)
```

#### Cart
```
GET    /api/cart                  - Get cart contents
POST   /api/cart                  - Add item to cart
PATCH  /api/cart/{product_id}     - Update item quantity
DELETE /api/cart/{product_id}     - Remove item from cart
DELETE /api/cart                  - Clear cart
```

### Example Requests

**Get products with filters:**
```bash
curl "http://localhost:8000/api/products?page=1&page_size=20&category_id=1&min_price=10&max_price=100&search=phone"
```

**Add item to cart:**
```bash
curl -X POST "http://localhost:8000/api/cart" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

**Create product:**
```bash
curl -X POST "http://localhost:8000/api/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "price": "99.99",
    "category_id": 1,
    "stock_quantity": 50
  }'
```

## 🗄️ Database Schema

### Products Table
```sql
- id: INTEGER (Primary Key)
- name: VARCHAR(255)
- description: TEXT
- price: NUMERIC(10,2)
- category_id: INTEGER (Foreign Key)
- image_url: VARCHAR(500)
- stock_quantity: INTEGER
- is_active: INTEGER (0/1)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Categories Table
```sql
- id: INTEGER (Primary Key)
- name: VARCHAR(100) UNIQUE
- description: TEXT
- slug: VARCHAR(100) UNIQUE
- is_active: INTEGER (0/1)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

## 🏗️ Project Structure
```
fastapi-shop/
├── backend/
│   ├── alembic/              # Database migrations
│   │   ├── versions/         # Migration files
│   │   └── env.py           # Alembic environment config
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── category.py
│   │   │   └── product.py
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── cart.py
│   │   │   ├── category.py
│   │   │   └── product.py
│   │   ├── routes/           # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── cart.py
│   │   │   ├── categories.py
│   │   │   └── products.py
│   │   ├── services/         # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── cart_service.py
│   │   │   ├── category_service.py
│   │   │   └── product_service.py
│   │   ├── repositories/     # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── category_repository.py
│   │   │   └── product_repository.py
│   │   ├── __init__.py
│   │   ├── cache.py          # Redis cache helper
│   │   ├── config.py         # Application configuration
│   │   ├── database.py       # Database setup & session
│   │   └── main.py           # FastAPI application entry
│   ├── static/               # Static files (images, etc.)
│   │   └── images/
│   ├── tests/                # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py       # Pytest fixtures
│   │   ├── test_products.py  # Product API tests
│   │   ├── test_categories.py # Category API tests
│   │   └── test_cart.py      # Cart API tests
│   ├── .env.example          # Environment variables template
│   ├── Dockerfile            # Backend Docker image
│   ├── alembic.ini           # Alembic configuration
│   ├── pytest.ini            # Pytest configuration
│   ├── requirements.txt      # Python dependencies
│   ├── run.py               # Development server runner
│   └── seed_data.py         # Database seeding script
├── frontend/                 # Vue.js application
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page views
│   │   ├── stores/          # Pinia stores
│   │   ├── router/          # Vue Router
│   │   ├── services/        # API service layer
│   │   └── main.js
│   ├── public/
│   ├── Dockerfile           # Frontend Docker image
│   ├── nginx.conf           # Frontend nginx config
│   ├── package.json
│   └── vite.config.js
├── nginx/                    # Main nginx configuration
│   └── nginx.conf
├── .gitignore
├── docker-compose.yml        # Docker services orchestration
├── deploy.sh                # Deployment script
└── README.md                # This file
```

## 📁 Key Files Description

### Backend Files

- **`run.py`** - Simple development server runner (alternative to uvicorn command)
- **`.env.example`** - Template for environment variables (copy to `.env`)
- **`requirements.txt`** - All Python dependencies
- **`alembic.ini`** - Database migration tool configuration
- **`pytest.ini`** - Test framework configuration
- **`seed_data.py`** - Script to populate database with sample data
- **`Dockerfile`** - Container image definition for backend

### Configuration Files

- **`app/config.py`** - Centralized application settings with Pydantic
- **`app/database.py`** - Async SQLAlchemy engine and session management
- **`app/cache.py`** - Redis connection and caching utilities
- **`app/main.py`** - FastAPI application with middleware and routes

### Testing Files

- **`conftest.py`** - Pytest fixtures and test database setup
- **`test_*.py`** - Test modules for each API component

### Docker Files

- **`docker-compose.yml`** - Multi-service orchestration (backend, frontend, postgres, redis, nginx)
- **`backend/Dockerfile`** - Backend Python/FastAPI image
- **`frontend/Dockerfile`** - Frontend Vue.js build image
- **`nginx/nginx.conf`** - Reverse proxy and load balancer config

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:
```env
# Application
APP_NAME=FastAPI Shop
DEBUG=True

# Database
POSTGRES_USER=fashop_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=fashop_db
DATABASE_URL=postgresql+asyncpg://fashop_user:your_secure_password@localhost:5432/fashop_db

# Redis
REDIS_PASSWORD=your_redis_password
REDIS_URL=redis://default:your_redis_password@localhost:6379/0

# Cache
CACHE_TTL=300

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🐳 Docker Services

The application consists of 5 Docker services:

1. **backend** - FastAPI application
2. **postgres** - PostgreSQL database
3. **redis** - Redis cache
4. **frontend** - Vue.js application
5. **nginx** - Reverse proxy

## 🚀 Docker Optimization

### Health Checks

All services include health checks for monitoring:
```bash
# Check service health
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' fashop_backend | jq
```

### Useful Docker Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild services
docker-compose up -d --build

# Execute command in container
docker-compose exec backend bash
```

## 📈 Performance Optimizations

- **Async I/O** - Non-blocking database and cache operations
- **Connection Pooling** - Reuse database connections (pool_size=10, max_overflow=20)
- **Redis Caching** - Cache frequently accessed data
- **Query Optimization** - Eager loading with joinedload/selectinload
- **Database Indexes** - Composite indexes on frequently queried columns
- **Pagination** - Limit result set size

## 🔒 Security Features

- **SQL Injection Protection** - Parameterized queries via SQLAlchemy
- **Input Validation** - Pydantic models with strict validation
- **CORS Configuration** - Controlled cross-origin requests
- **Cookie Security** - HttpOnly cookies for session management
- **Environment Variables** - Sensitive data in .env files
- **Soft Deletes** - Data preservation for audit trails

## 🚧 Known Limitations & Future Improvements

### Current Limitations
- No user authentication/authorization (uses anonymous sessions)
- No order management system
- No payment integration
- No email notifications
- Cart is session-based (not persistent per user)

## 📝 Development Notes

### Running Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

The project follows these principles:
- **Clean Architecture** - Separation of concerns
- **Type Hints** - Full type annotations
- **Async First** - Async/await throughout
- **DRY** - Don't Repeat Yourself
- **SOLID** - Object-oriented design principles

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes.

## 👤 Author

**Egor Pusto**
- GitHub: [@egorpusto](https://github.com/egorpusto)

## 🙏 Acknowledgments

- Original tutorial concept from [@septemberburned]
- FastAPI documentation and community
- SQLAlchemy team for excellent ORM
- All open-source contributors

---

**Note:** This project was initially created following a YouTube tutorial and subsequently enhanced with modern production practices, comprehensive testing, caching, async architecture, and additional features as a learning exercise and portfolio piece.