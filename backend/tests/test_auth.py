import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import crud, schemas, models
import uuid

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword",
            "is_super_admin": False,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert isinstance(data["id"], str)  # Should be UUID string
    assert len(data["id"]) == 36  # UUID format


def test_register_duplicate_email(client, db):
    """Test registration with duplicate email fails."""
    # Create first user
    user_data = schemas.UserCreate(
        name="First User", email="test@example.com", password="password123"
    )
    crud.create_user(db, user_data)

    # Try to create second user with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Second User",
            "email": "test@example.com",
            "password": "password456",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_user(client, db):
    """Test user login."""
    # Create user first
    user_data = schemas.UserCreate(
        name="Test User", email="test@example.com", password="testpassword"
    )
    crud.create_user(db, user_data)

    # Login with JSON format
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_protected_endpoint(client, db):
    """Test accessing protected endpoint with valid token."""
    # Create user and get token
    user_data = schemas.UserCreate(
        name="Test User", email="test@example.com", password="testpassword"
    )
    user = crud.create_user(db, user_data)

    # Login to get token with JSON format
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_protected_endpoint_no_token(client):
    """Test accessing protected endpoint without token."""
    # Generate a random UUID for the test
    test_user_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/users/{test_user_id}")
    # API returns 403 when no token is provided
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


def test_protected_endpoint_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    # Generate a random UUID for the test
    test_user_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/users/{test_user_id}",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


def test_me_endpoint(client, db):
    """Test /me endpoint to get current user profile."""
    # Create user first
    user_data = schemas.UserCreate(
        name="Test User", email="test@example.com", password="testpassword"
    )
    crud.create_user(db, user_data)

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    token = login_response.json()["access_token"]

    # Get current user profile
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


def test_me_endpoint_invalid_token(client):
    """Test /me endpoint with invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_me_endpoint_no_token(client):
    """Test /me endpoint without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]
