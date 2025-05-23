import pytest
from fastapi.testclient import TestClient
from app import crud, schemas, models


class TestCustomersRouter:
    def test_create_customer(self, client: TestClient, db):
        """Test creating a new customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Create customer
        customer_data = {
            "name": "Test Customer",
            "email": "customer@example.com",
            "phone": "+1234567890",
        }
        response = client.post(
            "/api/v1/customers/",
            json=customer_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        customer = response.json()
        assert customer["name"] == "Test Customer"
        assert customer["email"] == "customer@example.com"
        assert customer["phone"] == "+1234567890"
        assert "id" in customer
        assert "created_at" in customer
        assert "updated_at" in customer

    def test_create_customer_minimal_data(self, client: TestClient, db):
        """Test creating a customer with minimal required data."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Create customer with minimal data
        customer_data = {
            "name": "Minimal Customer",
            "email": "minimal@example.com",
        }
        response = client.post(
            "/api/v1/customers/",
            json=customer_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        customer = response.json()
        assert customer["name"] == "Minimal Customer"
        assert customer["email"] == "minimal@example.com"
        assert customer["phone"] is None

    def test_read_customers(self, client: TestClient, db):
        """Test getting all customers."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customers
        for i in range(3):
            customer_data = schemas.CustomerCreate(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                phone=f"+123456789{i}",
            )
            crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get all customers
        response = client.get(
            "/api/v1/customers/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        customers = response.json()
        assert len(customers) == 3

    def test_read_customers_pagination(self, client: TestClient, db):
        """Test customers pagination."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create multiple customers
        for i in range(10):
            customer_data = schemas.CustomerCreate(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                phone=f"+123456789{i}",
            )
            crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Test pagination
        response = client.get(
            "/api/v1/customers/?skip=2&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        customers = response.json()
        assert len(customers) == 3

    def test_read_customer(self, client: TestClient, db):
        """Test getting a specific customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
        )
        customer = crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get specific customer
        response = client.get(
            f"/api/v1/customers/{customer.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        customer_data = response.json()
        assert customer_data["id"] == customer.id
        assert customer_data["name"] == "Test Customer"
        assert customer_data["email"] == "customer@example.com"

    def test_read_customer_not_found(self, client: TestClient, db):
        """Test reading non-existent customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to read non-existent customer
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(
            f"/api/v1/customers/{non_existent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_update_customer(self, client: TestClient, db):
        """Test updating a customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customer
        customer_data = schemas.CustomerCreate(
            name="Original Customer",
            email="original@example.com",
            phone="+1234567890",
        )
        customer = crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Update customer
        update_data = {
            "name": "Updated Customer",
            "email": "updated@example.com",
            "phone": "+9876543210",
        }
        response = client.put(
            f"/api/v1/customers/{customer.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_customer = response.json()
        assert updated_customer["name"] == "Updated Customer"
        assert updated_customer["email"] == "updated@example.com"
        assert updated_customer["phone"] == "+9876543210"

    def test_update_customer_partial(self, client: TestClient, db):
        """Test partially updating a customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customer
        customer_data = schemas.CustomerCreate(
            name="Original Customer",
            email="original@example.com",
            phone="+1234567890",
        )
        customer = crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Update only name and phone
        update_data = {
            "name": "Partially Updated Customer",
            "phone": "+9876543210",
        }
        response = client.put(
            f"/api/v1/customers/{customer.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_customer = response.json()
        assert updated_customer["name"] == "Partially Updated Customer"
        assert (
            updated_customer["email"] == "original@example.com"
        )  # Should remain unchanged
        assert updated_customer["phone"] == "+9876543210"

    def test_update_customer_not_found(self, client: TestClient, db):
        """Test updating non-existent customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to update non-existent customer
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        update_data = {"name": "New Name"}
        response = client.put(
            f"/api/v1/customers/{non_existent_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_delete_customer(self, client: TestClient, db):
        """Test deleting a customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
        )
        customer = crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete customer
        response = client.delete(
            f"/api/v1/customers/{customer.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

        # Verify customer is deleted
        response = client.get(
            f"/api/v1/customers/{customer.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_delete_customer_not_found(self, client: TestClient, db):
        """Test deleting non-existent customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to delete non-existent customer
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        response = client.delete(
            f"/api/v1/customers/{non_existent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_unauthorized_access(self, client: TestClient):
        """Test that all endpoints require authentication."""
        # Test without token
        response = client.get("/api/v1/customers/")
        assert response.status_code == 403

        # Test other endpoints
        test_customer_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(f"/api/v1/customers/{test_customer_id}")
        assert response.status_code == 403

        response = client.post(
            "/api/v1/customers/", json={"name": "Test", "email": "test@example.com"}
        )
        assert response.status_code == 403

        response = client.put(
            f"/api/v1/customers/{test_customer_id}", json={"name": "Test"}
        )
        assert response.status_code == 403

        response = client.delete(f"/api/v1/customers/{test_customer_id}")
        assert response.status_code == 403

    def test_invalid_token(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        test_customer_id = "12345678-1234-1234-1234-123456789012"

        response = client.get(
            "/api/v1/customers/", headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401

        response = client.get(
            f"/api/v1/customers/{test_customer_id}",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

        response = client.post(
            "/api/v1/customers/",
            json={"name": "Test", "email": "test@example.com"},
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

        response = client.put(
            f"/api/v1/customers/{test_customer_id}",
            json={"name": "Test"},
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

        response = client.delete(
            f"/api/v1/customers/{test_customer_id}",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

    def test_create_customer_validation_errors(self, client: TestClient, db):
        """Test customer creation with invalid data."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Test missing required fields
        invalid_data = {"name": "Test Customer"}  # Missing email
        response = client.post(
            "/api/v1/customers/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

        # Test invalid email format
        invalid_data = {"name": "Test Customer", "email": "invalid-email"}
        response = client.post(
            "/api/v1/customers/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    def test_update_customer_validation_errors(self, client: TestClient, db):
        """Test customer update with invalid data."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Test invalid email format
        invalid_data = {"email": "invalid-email"}
        response = client.put(
            f"/api/v1/customers/{customer.id}",
            json=invalid_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
