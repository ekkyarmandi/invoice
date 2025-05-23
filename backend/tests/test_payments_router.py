import pytest
from fastapi.testclient import TestClient
from app import crud, schemas, models
from app.models.enums import InvoiceStatus, PaymentMethod, PaymentStatus


class TestPaymentsRouter:
    def test_create_payment(self, client: TestClient, db):
        """Test creating a new payment."""
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

        # Create an invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Create payment
        payment_data = {
            "invoice_id": invoice.id,
            "amount": 100.50,
            "method": "bank_transfer",
            "status": "completed",
        }
        response = client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        payment = response.json()
        assert payment["invoice_id"] == invoice.id
        assert payment["amount"] == 100.50
        assert payment["method"] == "bank_transfer"
        assert payment["status"] == "completed"
        assert payment["user_id"] == user.id
        assert "id" in payment
        assert "date" in payment

    def test_create_payment_with_nonexistent_invoice(self, client: TestClient, db):
        """Test creating a payment with a non-existent invoice."""
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

        # Try to create payment with non-existent invoice
        payment_data = {
            "invoice_id": "12345678-1234-1234-1234-123456789012",
            "amount": 100.50,
            "method": "bank_transfer",
            "status": "completed",
        }
        response = client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_create_payment_forbidden_for_other_user_invoice(
        self, client: TestClient, db
    ):
        """Test that users cannot create payments for other users' invoices."""
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
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to create payment for user1's invoice
        payment_data = {
            "invoice_id": invoice.id,
            "amount": 100.50,
            "method": "bank_transfer",
            "status": "completed",
        }
        response = client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_read_payments_as_regular_user(self, client: TestClient, db):
        """Test that regular users only see their own payments."""
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
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice1 = crud.create_invoice(db, invoice1_data, user1.id)

        invoice2_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice2 = crud.create_invoice(db, invoice2_data, user2.id)

        # Create payments for both users
        payment1_data = schemas.PaymentCreate(
            invoice_id=invoice1.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment1 = crud.create_payment(db, payment1_data, user1.id)

        payment2_data = schemas.PaymentCreate(
            invoice_id=invoice2.id,
            amount=200.0,
            method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
        )
        payment2 = crud.create_payment(db, payment2_data, user2.id)

        # Login as user1
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get payments - should only see user1's payment
        response = client.get(
            "/api/v1/payments/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        payments = response.json()
        assert len(payments) == 1
        assert payments[0]["id"] == payment1.id

    def test_read_payments_as_super_admin(self, client: TestClient, db):
        """Test that super admin can see all payments."""
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
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice1 = crud.create_invoice(db, invoice1_data, user.id)

        invoice2_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice2 = crud.create_invoice(db, invoice2_data, super_admin.id)

        # Create payments for both users
        payment1_data = schemas.PaymentCreate(
            invoice_id=invoice1.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment1 = crud.create_payment(db, payment1_data, user.id)

        payment2_data = schemas.PaymentCreate(
            invoice_id=invoice2.id,
            amount=200.0,
            method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
        )
        payment2 = crud.create_payment(db, payment2_data, super_admin.id)

        # Login as super admin
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )
        token = login_response.json()["access_token"]

        # Get payments - should see all payments
        response = client.get(
            "/api/v1/payments/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        payments = response.json()
        assert len(payments) == 2

    def test_read_payments_with_invoice_filter(self, client: TestClient, db):
        """Test filtering payments by invoice ID."""
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
        invoice1_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice1 = crud.create_invoice(db, invoice1_data, user.id)

        invoice2_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice2 = crud.create_invoice(db, invoice2_data, user.id)

        # Create payments for both invoices
        payment1_data = schemas.PaymentCreate(
            invoice_id=invoice1.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment1 = crud.create_payment(db, payment1_data, user.id)

        payment2_data = schemas.PaymentCreate(
            invoice_id=invoice2.id,
            amount=200.0,
            method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
        )
        payment2 = crud.create_payment(db, payment2_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get payments filtered by invoice1
        response = client.get(
            f"/api/v1/payments/?invoice_id={invoice1.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        payments = response.json()
        assert len(payments) == 1
        assert payments[0]["id"] == payment1.id

    def test_read_payments_pagination(self, client: TestClient, db):
        """Test payments pagination."""
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

        # Create an invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Create multiple payments
        for i in range(10):
            payment_data = schemas.PaymentCreate(
                invoice_id=invoice.id,
                amount=float(i * 10),
                method=PaymentMethod.BANK_TRANSFER,
                status=PaymentStatus.COMPLETED,
            )
            crud.create_payment(db, payment_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Test pagination
        response = client.get(
            "/api/v1/payments/?skip=2&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        payments = response.json()
        assert len(payments) == 3

    def test_read_payment(self, client: TestClient, db):
        """Test getting a specific payment."""
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

        # Create an invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Create payment
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment = crud.create_payment(db, payment_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Get specific payment
        response = client.get(
            f"/api/v1/payments/{payment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        payment_response = response.json()
        assert payment_response["id"] == payment.id
        assert payment_response["invoice_id"] == invoice.id
        assert payment_response["user_id"] == user.id

    def test_read_payment_forbidden_for_other_user(self, client: TestClient, db):
        """Test that users cannot read other users' payments."""
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
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Create payment for user1
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment = crud.create_payment(db, payment_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to read user1's payment
        response = client.get(
            f"/api/v1/payments/{payment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_read_payment_not_found(self, client: TestClient, db):
        """Test reading non-existent payment."""
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

        # Try to read non-existent payment
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(
            f"/api/v1/payments/{non_existent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_update_payment(self, client: TestClient, db):
        """Test updating a payment."""
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

        # Create an invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Create payment
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
        )
        payment = crud.create_payment(db, payment_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Update payment
        update_data = {"amount": 150.75, "method": "credit_card", "status": "completed"}
        response = client.put(
            f"/api/v1/payments/{payment.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        updated_payment = response.json()
        assert updated_payment["amount"] == 150.75
        assert updated_payment["method"] == "credit_card"
        assert updated_payment["status"] == "completed"

    def test_update_payment_forbidden_for_other_user(self, client: TestClient, db):
        """Test that users cannot update other users' payments."""
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
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Create payment for user1
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
        )
        payment = crud.create_payment(db, payment_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to update user1's payment
        update_data = {"status": "completed"}
        response = client.put(
            f"/api/v1/payments/{payment.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_update_payment_not_found(self, client: TestClient, db):
        """Test updating non-existent payment."""
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

        # Try to update non-existent payment
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        update_data = {"status": "completed"}
        response = client.put(
            f"/api/v1/payments/{non_existent_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_delete_payment(self, client: TestClient, db):
        """Test deleting a payment."""
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

        # Create an invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Create payment
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment = crud.create_payment(db, payment_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete payment
        response = client.delete(
            f"/api/v1/payments/{payment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

        # Verify payment is deleted
        response = client.get(
            f"/api/v1/payments/{payment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_delete_payment_forbidden_for_other_user(self, client: TestClient, db):
        """Test that users cannot delete other users' payments."""
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
            customer_id=customer.id, status=InvoiceStatus.SENT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user1.id)

        # Create payment for user1
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.COMPLETED,
        )
        payment = crud.create_payment(db, payment_data, user1.id)

        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Try to delete user1's payment
        response = client.delete(
            f"/api/v1/payments/{payment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_delete_payment_not_found(self, client: TestClient, db):
        """Test deleting non-existent payment."""
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

        # Try to delete non-existent payment
        non_existent_id = "12345678-1234-1234-1234-123456789012"
        response = client.delete(
            f"/api/v1/payments/{non_existent_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_unauthorized_access(self, client: TestClient):
        """Test that all endpoints require authentication."""
        # Test without token
        response = client.get("/api/v1/payments/")
        assert response.status_code == 403

        # Test other endpoints
        test_payment_id = "12345678-1234-1234-1234-123456789012"
        test_invoice_id = "12345678-1234-1234-1234-123456789012"

        response = client.get(f"/api/v1/payments/{test_payment_id}")
        assert response.status_code == 403

        response = client.post(
            "/api/v1/payments/", json={"invoice_id": test_invoice_id, "amount": 100}
        )
        assert response.status_code == 403

        response = client.put(
            f"/api/v1/payments/{test_payment_id}", json={"amount": 200}
        )
        assert response.status_code == 403

        response = client.delete(f"/api/v1/payments/{test_payment_id}")
        assert response.status_code == 403

    def test_invalid_token(self, client: TestClient):
        """Test that all endpoints reject invalid tokens."""
        headers = {"Authorization": "Bearer invalid_token"}

        # Test various endpoints with invalid token
        response = client.get("/api/v1/payments/", headers=headers)
        assert response.status_code == 401

        test_payment_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(f"/api/v1/payments/{test_payment_id}", headers=headers)
        assert response.status_code == 401

        response = client.put(
            f"/api/v1/payments/{test_payment_id}",
            headers=headers,
            json={"amount": 100.0},
        )
        assert response.status_code == 401

        response = client.delete(f"/api/v1/payments/{test_payment_id}", headers=headers)
        assert response.status_code == 401

    def test_delete_payment_crud_failure(self, client: TestClient, db):
        """Test deleting a payment where CRUD operation fails."""
        # Create user, customer, and invoice
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="password",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=InvoiceStatus.SENT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Create payment
        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
        )
        payment = crud.create_payment(db, payment_data, user.id)

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login_response.json()["access_token"]

        # Delete the payment first using CRUD
        crud.delete_payment(db, payment.id)

        # Try to delete the already deleted payment via API (should fail)
        response = client.delete(
            f"/api/v1/payments/{payment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "Payment not found" in response.json()["detail"]
