# Invoice Management System - Backend

A comprehensive FastAPI-based backend for managing invoices, customers, and payments with SQLite database support.

## Features

- **User Management**: Registration, authentication, and authorization with JWT tokens
- **Customer Management**: Create, read, update, and delete customers/clients
- **Invoice Management**: Full CRUD operations for invoices with line items
- **Payment Management**: Track and manage invoice payments
- **Role-based Access Control**: Regular users and super admin roles
- **Database Migrations**: Alembic for database schema management
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Testing**: Comprehensive unit tests with pytest

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Python SQL toolkit and ORM
- **SQLite**: Lightweight database for development
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **Passlib**: Password hashing library
- **Python-Jose**: JWT token handling
- **Pytest**: Testing framework

## Database Schema

Based on the Entity Relationship Diagram (ERD), the system includes:

- **Users**: Application users with admin privileges support
- **Customers**: Customer/client information with type classification
- **Invoices**: Invoice records with status tracking and payment flags
- **Invoice Items**: Individual line items for each invoice
- **Payments**: Payment records linked to invoices and users

## Setup Instructions

### Prerequisites

- Python 3.10+
- uv (pip alternative) or pip

### Installation

1. **Clone the repository and navigate to backend:**

   ```bash
   cd backend
   ```

2. **Activate virtual environment:**

   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   uv sync  # or pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize database:**

   ```bash
   alembic init alembic  # If not already done
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user profile

### Users

- `GET /api/v1/users/` - List all users (Super admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (Super admin only)

### Customers

- `POST /api/v1/customers/` - Create customer
- `GET /api/v1/customers/` - List customers
- `GET /api/v1/customers/{customer_id}` - Get customer by ID
- `PUT /api/v1/customers/{customer_id}` - Update customer
- `DELETE /api/v1/customers/{customer_id}` - Delete customer

### Invoices

- `POST /api/v1/invoices/` - Create invoice
- `GET /api/v1/invoices/` - List invoices
- `GET /api/v1/invoices/{invoice_id}` - Get invoice by ID
- `PUT /api/v1/invoices/{invoice_id}` - Update invoice
- `DELETE /api/v1/invoices/{invoice_id}` - Delete invoice
- `POST /api/v1/invoices/{invoice_id}/items` - Add invoice item
- `PUT /api/v1/invoices/items/{item_id}` - Update invoice item
- `DELETE /api/v1/invoices/items/{item_id}` - Delete invoice item

### Payments

- `POST /api/v1/payments/` - Create payment
- `GET /api/v1/payments/` - List payments
- `GET /api/v1/payments/{payment_id}` - Get payment by ID
- `PUT /api/v1/payments/{payment_id}` - Update payment
- `DELETE /api/v1/payments/{payment_id}` - Delete payment

## Authentication

The API uses JWT Bearer tokens for authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your-token>
```

## Database Migrations

Use Alembic for database schema changes:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## Testing & Code Coverage

This project maintains **99% test coverage** with comprehensive unit tests for all routers, models, and CRUD operations.

### Quick Start

```bash
# Activate virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run all tests with coverage
uv run coverage run -m pytest tests/ -v

# Generate coverage report
uv run coverage report -m

# Generate HTML coverage report
uv run coverage html
```

### Coverage Analysis Commands

#### 1. Basic Coverage Reports

```bash
# Text coverage report with missing lines
uv run coverage report -m

# Router-specific coverage
uv run coverage report -m --include="app/routers/*"

# Model-specific coverage
uv run coverage report -m --include="app/models/*"

# CRUD-specific coverage
uv run coverage report -m --include="app/crud.py"
```

#### 2. HTML Coverage Report

The HTML report provides the most detailed view of coverage:

```bash
# Generate HTML report
uv run coverage html

# Open in browser (macOS)
open htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html

# Open in browser (Windows)
start htmlcov/index.html
```

#### 3. Investigating Missing Coverage

**Find specific missing lines:**

```bash
# Check specific lines in a file
sed -n '75p;120p;180p;210p' app/routers/invoices.py

# Get context around missing lines
sed -n '73,77p;118,122p' app/routers/invoices.py

# Search for specific patterns in missing lines
grep -n "raise HTTPException" app/routers/invoices.py
```

**Identify uncovered code patterns:**

```bash
# Find all error handling blocks
grep -n "raise HTTPException" app/routers/*.py

# Find all return statements
grep -n "return" app/routers/*.py

# Find CRUD operations that might fail
grep -n "crud\." app/routers/*.py
```

#### 4. Advanced Coverage Analysis

**Coverage by file type:**

```bash
# Only test files coverage
uv run coverage report -m --include="tests/*"

# Exclude test files from coverage
uv run coverage report -m --omit="tests/*"

# Router coverage sorted by missing lines
uv run coverage report -m --include="app/routers/*" --sort=miss
```

**Coverage data manipulation:**

```bash
# Combine multiple coverage runs
uv run coverage combine

# Erase previous coverage data
uv run coverage erase

# Show coverage data info
uv run coverage debug data
```

### Test Organization

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication endpoint tests
├── test_crud.py            # CRUD operations tests
├── test_customers_router.py # Customer endpoint tests
├── test_invoices_router.py  # Invoice endpoint tests
├── test_payments_router.py  # Payment endpoint tests
└── test_users_router.py     # User endpoint tests
```

### Writing Effective Tests

#### Test Categories Covered

1. **Happy Path Tests**: Normal operation scenarios
2. **Error Handling Tests**: Invalid inputs and edge cases
3. **Permission Tests**: Authorization and access control
4. **CRUD Failure Tests**: Database operation failures
5. **Authentication Tests**: Token validation and security

#### Coverage Goals by Component

- **Routers**: 95-100% (API endpoints)
- **CRUD Operations**: 100% (Database operations)
- **Models**: 80-90% (Model methods and properties)
- **Authentication**: 90-95% (Security functions)

#### Example Test Patterns

**Testing Router Endpoints:**

```python
def test_endpoint_success(self, client: TestClient, db):
    """Test successful operation"""
    # Setup test data
    # Make API request
    # Assert response and side effects

def test_endpoint_not_found(self, client: TestClient, db):
    """Test resource not found scenario"""
    # Test with non-existent resource ID

def test_endpoint_permission_denied(self, client: TestClient, db):
    """Test insufficient permissions"""
    # Login as regular user, try to access admin resource

def test_endpoint_crud_failure(self, client: TestClient, db):
    """Test CRUD operation failure"""
    # Delete resource via CRUD, then try to operate on it via API
```

### Troubleshooting Coverage Issues

#### Common Uncovered Scenarios

1. **Error Handling**: Missing tests for exception paths
2. **Permission Checks**: Missing tests for access control
3. **Edge Cases**: Boundary conditions and race conditions
4. **Return Statements**: Final return statements in error handlers

#### Finding Hard-to-Cover Lines

```bash
# Find lines that are only covered by error paths
uv run coverage report -m --show-missing

# Use HTML report to visualize control flow
uv run coverage html
# Look for red lines in htmlcov/

# Check if lines are unreachable code
sed -n 'LINE_NUMBERp' app/routers/target_file.py
```

#### Debugging Test Coverage

```bash
# Run single test file with coverage
uv run coverage run -m pytest tests/test_invoices_router.py -v
uv run coverage report -m --include="app/routers/invoices.py"

# Run specific test method
uv run coverage run -m pytest tests/test_invoices_router.py::TestInvoicesRouter::test_specific_method -v

# Combine with previous coverage data
uv run coverage run --append -m pytest tests/test_auth.py -v
```

### Coverage Best Practices

1. **Target 95-100% for core business logic** (routers, CRUD)
2. **80-90% for supporting code** (models, utilities)
3. **Don't chase 100% blindly** - some edge cases aren't worth complex mocking
4. **Focus on meaningful tests** over coverage percentage
5. **Use HTML reports** for visual coverage analysis
6. **Test error paths** as thoroughly as success paths
7. **Cover permission and security scenarios** comprehensively

### Continuous Integration

For CI/CD pipelines, use these commands:

```bash
# Run tests with coverage and fail if below threshold
uv run coverage run -m pytest tests/
uv run coverage report --fail-under=95

# Generate XML report for CI tools
uv run coverage xml

# Generate JSON report for analysis tools
uv run coverage json
```

### Current Coverage Stats

- **Overall Coverage**: 99%
- **Router Coverage**: 98% (216 statements, 5 missing)
- **CRUD Coverage**: 100%
- **Test Files**: 126 tests across 6 test files

**Router-specific Coverage:**

- `auth.py`: 100%
- `customers.py`: 100%
- `users.py`: 100%
- `invoices.py`: 95%
- `payments.py`: 98%

The remaining 1% consists of edge cases in error handling that would require complex mocking to test meaningfully.

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./invoice_app.db

# Security Configuration
SECRET_KEY=your-secret-key-change-this-in-production

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Development Settings
DEBUG=True
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── auth.py              # Authentication utilities
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── auth.py
│       ├── users.py
│       ├── customers.py
│       ├── invoices.py
│       └── payments.py
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── requirements.txt         # Dependencies
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

## Development Notes

- The application automatically creates database tables on startup
- SQLite database file (`invoice_app.db`) will be created in the backend directory
- Use Alembic for production database migrations
- Super admin users can access all resources; regular users can only access their own data
- Invoice totals are automatically calculated based on line items
- Payment status affects invoice payment tracking

## Production Deployment

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Set strong SECRET_KEY in environment variables
3. Configure proper CORS origins
4. Use a reverse proxy (nginx)
5. Set up proper logging
6. Use environment-specific configuration
