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

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

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
