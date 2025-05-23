import pytest
from fastapi.testclient import TestClient
from app import crud, schemas, models
from app.models.enums import InvoiceStatus


class TestInvoicesRouter:
    def test_create_invoice(self, client: TestClient, db):
        """Test creating a new invoice."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
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

        # Create invoice with items
        invoice_data = {
            "customer_id": customer.id,
            "status": "draft",
            "items": [
                {"description": "Item 1", "quantity": 2, "unit_price": 10.50},
                {"description": "Item 2", "quantity": 1, "unit_price": 25.00},
            ],
        }
        response = client.post(
            "/api/v1/invoices/",
            json=invoice_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        invoice = response.json()
        assert invoice["customer_id"] == customer.id
        assert invoice["status"] == "draft"
        assert invoice["user_id"] == user.id
        assert len(invoice["items"]) == 2
        assert invoice["total_amount"] == 46.0  # (2 * 10.50) + (1 * 25.00)
        assert "id" in invoice
        assert "date" in invoice

    def test_create_invoice_with_nonexistent_customer(self, client: TestClient, db):
        """Test creating an invoice with a non-existent customer."""
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

        # Try to create invoice with non-existent customer
        invoice_data = {
            "customer_id": "12345678-1234-1234-1234-123456789012",
            "status": "draft",
            "items": [],
        }
        response = client.post(
            "/api/v1/invoices/",
            json=invoice_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_read_invoices_as_regular_user(self, client: TestClient, db):
        """Test that regular users only see their own invoices."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoices for both users
        invoice1_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice1 = crud.create_invoice(db, invoice1_data, user1.id)

        invoice2_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice2 = crud.create_invoice(db, invoice2_data, user2.id)

        # Login as user1
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get invoices - should only see user1's invoice
        response = client.get(
            "/api/v1/invoices/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        invoices = response.json()
        assert len(invoices) == 1
        assert invoices[0]["id"] == invoice1.id

    def test_read_invoices_as_super_admin(self, client: TestClient, db):
        """Test that super admin can see all invoices."""
        # Create users
        super_admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@example.com",
            password="adminpassword",
            is_super_admin=True,
        )
        super_admin = crud.create_user(db, super_admin_data)

        user_data = schemas.UserCreate(
            name="Regular User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoices for both users
        invoice1_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice1 = crud.create_invoice(db, invoice1_data, user.id)

        invoice2_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice2 = crud.create_invoice(db, invoice2_data, super_admin.id)

        # Login as super admin
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Get invoices - should see all invoices
        response = client.get(
            "/api/v1/invoices/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        invoices = response.json()
        assert len(invoices) == 2

    def test_read_invoices_pagination(self, client: TestClient, db):
        """Test invoices pagination."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create multiple invoices
        for i in range(10):
            invoice_data = schemas.InvoiceCreate(
                customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
            )
            crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Test pagination
        response = client.get(
            "/api/v1/invoices/?skip=2&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        invoices = response.json()
        assert len(invoices) == 3

    def test_read_invoice(self, client: TestClient, db):
        """Test getting a specific invoice."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get specific invoice
        response = client.get(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        invoice_response = response.json()
        assert invoice_response["id"] == invoice.id
        assert invoice_response["customer_id"] == customer.id
        assert invoice_response["user_id"] == user.id

    def test_read_invoice_forbidden_for_other_user(self, client: TestClient, db):
        """Test that users cannot read other users' invoices."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice for user1
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to read user1's invoice
        response = client.get(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_read_invoice_not_found(self, client: TestClient, db):
        """Test reading non-existent invoice."""
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

        # Try to read non-existent invoice
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(
            f"/api/v1/invoices/{non_existent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_update_invoice(self, client: TestClient, db):
        """Test updating an invoice."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create customers
        customer1_data = schemas.CustomerCreate(
            name="Customer 1",
            email="customer1@example.com",
        )
        customer1 = crud.create_customer(db, customer1_data)

        customer2_data = schemas.CustomerCreate(
            name="Customer 2",
            email="customer2@example.com",
        )
        customer2 = crud.create_customer(db, customer2_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer1.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Update invoice
        update_data = {"customer_id": customer2.id, "status": "sent"}
        response = client.put(
            f"/api/v1/invoices/{invoice.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_invoice = response.json()
        assert updated_invoice["customer_id"] == customer2.id
        assert updated_invoice["status"] == "sent"

    def test_update_invoice_with_nonexistent_customer(self, client: TestClient, db):
        """Test updating an invoice with a non-existent customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to update with non-existent customer
        update_data = {"customer_id": "12345678-1234-1234-1234-123456789012"}
        response = client.put(
            f"/api/v1/invoices/{invoice.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_update_invoice_forbidden_for_other_user(self, client: TestClient, db):
        """Test that users cannot update other users' invoices."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice for user1
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to update user1's invoice
        update_data = {"status": "sent"}
        response = client.put(
            f"/api/v1/invoices/{invoice.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_delete_invoice(self, client: TestClient, db):
        """Test deleting an invoice."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete invoice
        response = client.delete(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

        # Verify invoice is deleted
        response = client.get(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_delete_invoice_forbidden_for_other_user(self, client: TestClient, db):
        """Test that users cannot delete other users' invoices."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice for user1
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to delete user1's invoice
        response = client.delete(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    # Invoice Items Tests
    def test_create_invoice_item(self, client: TestClient, db):
        """Test adding an item to an invoice."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Add item to invoice
        item_data = {"description": "Test Item", "quantity": 3, "unit_price": 15.75}
        response = client.post(
            f"/api/v1/invoices/{invoice.id}/items",
            json=item_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        item = response.json()
        assert item["description"] == "Test Item"
        assert item["quantity"] == 3
        assert item["unit_price"] == 15.75
        assert item["total"] == 47.25  # 3 * 15.75
        assert item["invoice_id"] == invoice.id

    def test_update_invoice_item(self, client: TestClient, db):
        """Test updating an invoice item."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice with item
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Original Item", quantity=1, unit_price=10.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)
        item = invoice.items[0]

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Update item
        update_data = {"description": "Updated Item", "quantity": 2, "unit_price": 20.0}
        response = client.put(
            f"/api/v1/invoices/items/{item.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_item = response.json()
        assert updated_item["description"] == "Updated Item"
        assert updated_item["quantity"] == 2
        assert updated_item["unit_price"] == 20.0
        assert updated_item["total"] == 40.0

    def test_delete_invoice_item(self, client: TestClient, db):
        """Test deleting an invoice item."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice with item
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=10.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)
        item = invoice.items[0]

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete item
        response = client.delete(
            f"/api/v1/invoices/items/{item.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

    def test_unauthorized_access(self, client: TestClient):
        """Test that all endpoints require authentication."""
        # Test without token
        response = client.get("/api/v1/invoices/")
        assert response.status_code == 403

        # Test other endpoints
        test_invoice_id = "12345678-1234-1234-1234-123456789012"
        test_item_id = "12345678-1234-1234-1234-123456789012"

        response = client.get(f"/api/v1/invoices/{test_invoice_id}")
        assert response.status_code == 403

        response = client.post(
            "/api/v1/invoices/", json={"customer_id": test_invoice_id}
        )
        assert response.status_code == 403

        response = client.put(
            f"/api/v1/invoices/{test_invoice_id}", json={"status": "sent"}
        )
        assert response.status_code == 403

        response = client.delete(f"/api/v1/invoices/{test_invoice_id}")
        assert response.status_code == 403

        # Invoice items
        response = client.post(
            f"/api/v1/invoices/{test_invoice_id}/items", json={"description": "Test"}
        )
        assert response.status_code == 403

        response = client.put(
            f"/api/v1/invoices/items/{test_item_id}", json={"description": "Test"}
        )
        assert response.status_code == 403

        response = client.delete(f"/api/v1/invoices/items/{test_item_id}")
        assert response.status_code == 403

    def test_invalid_token(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        test_invoice_id = "12345678-1234-1234-1234-123456789012"
        test_item_id = "12345678-1234-1234-1234-123456789012"

        response = client.get(
            "/api/v1/invoices/", headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401

        response = client.get(
            f"/api/v1/invoices/{test_invoice_id}",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

        response = client.post(
            "/api/v1/invoices/",
            json={"customer_id": test_invoice_id},
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

    def test_update_invoice_with_invalid_customer(self, client: TestClient, db):
        """Test updating an invoice with non-existent customer."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to update with non-existent customer
        response = client.put(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"customer_id": "nonexistent-id"},
        )
        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]

    def test_update_invoice_item_not_found_after_permission_check(
        self, client: TestClient, db
    ):
        """Test updating an invoice item where update operation fails."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice with item
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=10.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)
        item = invoice.items[0]

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete the item first to make the next update fail
        crud.delete_invoice_item(db, item.id)

        # Try to update the deleted item (should fail)
        response = client.put(
            f"/api/v1/invoices/items/{item.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "Updated Item"},
        )
        assert response.status_code == 404
        assert "Invoice item not found" in response.json()["detail"]

    def test_delete_invoice_item_crud_failure(self, client: TestClient, db):
        """Test deleting an invoice item where CRUD operation fails."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice with item
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=10.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)
        item = invoice.items[0]

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete the item first using CRUD
        crud.delete_invoice_item(db, item.id)

        # Try to delete the already deleted item via API (should fail)
        response = client.delete(
            f"/api/v1/invoices/items/{item.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "Invoice item not found" in response.json()["detail"]

    def test_delete_invoice_crud_failure(self, client: TestClient, db):
        """Test deleting an invoice where CRUD operation fails."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        # Create a customer
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete the invoice first using CRUD
        crud.delete_invoice(db, invoice.id)

        # Try to delete the already deleted invoice via API (should fail)
        response = client.delete(
            f"/api/v1/invoices/{invoice.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "Invoice not found" in response.json()["detail"]

    def test_create_invoice_item_invoice_not_found(self, client: TestClient, db):
        """Test creating an item for non-existent invoice."""
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

        # Try to create item for non-existent invoice
        response = client.post(
            "/api/v1/invoices/nonexistent-id/items",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "Test Item", "quantity": 1, "unit_price": 10.0},
        )
        assert response.status_code == 404
        assert "Invoice not found" in response.json()["detail"]

    def test_create_invoice_item_permission_denied(self, client: TestClient, db):
        """Test creating an item for another user's invoice."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create customer and invoice for user1
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to create item for user1's invoice
        response = client.post(
            f"/api/v1/invoices/{invoice.id}/items",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "Test Item", "quantity": 1, "unit_price": 10.0},
        )
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    def test_update_invoice_item_permission_denied(self, client: TestClient, db):
        """Test updating an item from another user's invoice."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create customer and invoice with item for user1
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=10.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)
        item = invoice.items[0]

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to update user1's invoice item
        response = client.put(
            f"/api/v1/invoices/items/{item.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "Updated Item"},
        )
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    def test_delete_invoice_item_permission_denied(self, client: TestClient, db):
        """Test deleting an item from another user's invoice."""
        # Create users
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="password",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="password",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        # Create customer and invoice with item for user1
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=10.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)
        item = invoice.items[0]

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to delete user1's invoice item
        response = client.delete(
            f"/api/v1/invoices/items/{item.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
