import pytest
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.auth import get_password_hash


class TestUserCRUD:
    def test_create_user(self, db: Session):
        """Test creating a user."""
        user_data = schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        assert user.name == user_data.name
        assert user.email == user_data.email
        assert user.is_super_admin == user_data.is_super_admin
        assert user.password_hash != user_data.password
        assert user.id is not None

    def test_get_user(self, db: Session):
        """Test getting a user by ID."""
        # Create a user first
        user_data = schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        created_user = crud.create_user(db, user_data)

        # Get the user
        retrieved_user = crud.get_user(db, created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    def test_get_user_not_found(self, db: Session):
        """Test getting a user that doesn't exist."""
        user = crud.get_user(db, "nonexistent-id")
        assert user is None

    def test_get_user_by_email(self, db: Session):
        """Test getting a user by email."""
        user_data = schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        created_user = crud.create_user(db, user_data)

        retrieved_user = crud.get_user_by_email(db, "test@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id

    def test_get_user_by_email_not_found(self, db: Session):
        """Test getting a user by email that doesn't exist."""
        user = crud.get_user_by_email(db, "nonexistent@example.com")
        assert user is None

    def test_get_users(self, db: Session):
        """Test getting all users with pagination."""
        # Create multiple users
        for i in range(5):
            user_data = schemas.UserCreate(
                name=f"Test User {i}",
                email=f"test{i}@example.com",
                password="testpassword",
                is_super_admin=False,
            )
            crud.create_user(db, user_data)

        # Get all users
        users = crud.get_users(db, skip=0, limit=10)
        assert len(users) == 5

        # Test pagination
        users_page = crud.get_users(db, skip=2, limit=2)
        assert len(users_page) == 2

    def test_update_user(self, db: Session):
        """Test updating a user."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        created_user = crud.create_user(db, user_data)

        # Update the user
        update_data = schemas.UserUpdate(name="Updated Name")
        updated_user = crud.update_user(db, created_user.id, update_data)

        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        assert updated_user.email == created_user.email

    def test_update_user_not_found(self, db: Session):
        """Test updating a user that doesn't exist."""
        update_data = schemas.UserUpdate(name="Updated Name")
        result = crud.update_user(db, "nonexistent-id", update_data)
        assert result is None

    def test_delete_user(self, db: Session):
        """Test deleting a user."""
        # Create a user
        user_data = schemas.UserCreate(
            name="Test User",
            email="test@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        created_user = crud.create_user(db, user_data)

        # Delete the user
        result = crud.delete_user(db, created_user.id)
        assert result is True

        # Verify user is deleted
        deleted_user = crud.get_user(db, created_user.id)
        assert deleted_user is None

    def test_delete_user_not_found(self, db: Session):
        """Test deleting a user that doesn't exist."""
        result = crud.delete_user(db, "nonexistent-id")
        assert result is False


class TestCustomerCRUD:
    def test_create_customer(self, db: Session):
        """Test creating a customer."""
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        assert customer.name == customer_data.name
        assert customer.email == customer_data.email
        assert customer.phone == customer_data.phone
        assert customer.type == customer_data.type
        assert customer.id is not None

    def test_get_customer(self, db: Session):
        """Test getting a customer by ID."""
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        created_customer = crud.create_customer(db, customer_data)

        retrieved_customer = crud.get_customer(db, created_customer.id)
        assert retrieved_customer is not None
        assert retrieved_customer.id == created_customer.id

    def test_get_customer_not_found(self, db: Session):
        """Test getting a customer that doesn't exist."""
        customer = crud.get_customer(db, "nonexistent-id")
        assert customer is None

    def test_get_customers(self, db: Session):
        """Test getting all customers with pagination."""
        # Create multiple customers
        for i in range(3):
            customer_data = schemas.CustomerCreate(
                name=f"Test Customer {i}",
                email=f"customer{i}@example.com",
                phone=f"+123456789{i}",
                type=models.CustomerType.CUSTOMER,
            )
            crud.create_customer(db, customer_data)

        customers = crud.get_customers(db, skip=0, limit=10)
        assert len(customers) == 3

    def test_update_customer(self, db: Session):
        """Test updating a customer."""
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        created_customer = crud.create_customer(db, customer_data)

        update_data = schemas.CustomerUpdate(name="Updated Customer")
        updated_customer = crud.update_customer(db, created_customer.id, update_data)

        assert updated_customer is not None
        assert updated_customer.name == "Updated Customer"

    def test_update_customer_not_found(self, db: Session):
        """Test updating a customer that doesn't exist."""
        update_data = schemas.CustomerUpdate(name="Updated Customer")
        result = crud.update_customer(db, "nonexistent-id", update_data)
        assert result is None

    def test_delete_customer(self, db: Session):
        """Test deleting a customer."""
        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        created_customer = crud.create_customer(db, customer_data)

        result = crud.delete_customer(db, created_customer.id)
        assert result is True

        deleted_customer = crud.get_customer(db, created_customer.id)
        assert deleted_customer is None

    def test_delete_customer_not_found(self, db: Session):
        """Test deleting a customer that doesn't exist."""
        result = crud.delete_customer(db, "nonexistent-id")
        assert result is False


class TestInvoiceCRUD:
    def test_create_invoice(self, db: Session):
        """Test creating an invoice with items."""
        # Create user and customer first
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoice
        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item 1", quantity=2, unit_price=100.0
                ),
                schemas.InvoiceItemCreate(
                    description="Test Item 2", quantity=1, unit_price=50.0
                ),
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        assert invoice.customer_id == customer.id
        assert invoice.user_id == user.id
        assert invoice.status == models.InvoiceStatus.DRAFT
        assert invoice.total_amount == 250.0  # (2*100) + (1*50)
        assert len(invoice.items) == 2

    def test_get_invoice(self, db: Session):
        """Test getting an invoice by ID."""
        # Create user and customer first
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        created_invoice = crud.create_invoice(db, invoice_data, user.id)

        retrieved_invoice = crud.get_invoice(db, created_invoice.id)
        assert retrieved_invoice is not None
        assert retrieved_invoice.id == created_invoice.id

    def test_get_invoice_not_found(self, db: Session):
        """Test getting an invoice that doesn't exist."""
        invoice = crud.get_invoice(db, "nonexistent-id")
        assert invoice is None

    def test_get_invoices(self, db: Session):
        """Test getting all invoices with optional user filter."""
        # Create users and customer
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        user2_data = schemas.UserCreate(
            name="User 2",
            email="user2@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user2 = crud.create_user(db, user2_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoices for different users
        for i in range(2):
            invoice_data = schemas.InvoiceCreate(
                customer_id=customer.id,
                status=models.InvoiceStatus.DRAFT,
                items=[
                    schemas.InvoiceItemCreate(
                        description=f"Test Item {i}", quantity=1, unit_price=100.0
                    )
                ],
            )
            crud.create_invoice(db, invoice_data, user1.id)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item for User 2", quantity=1, unit_price=100.0
                )
            ],
        )
        crud.create_invoice(db, invoice_data, user2.id)

        # Get all invoices
        all_invoices = crud.get_invoices(db)
        assert len(all_invoices) == 3

        # Get invoices for specific user
        user1_invoices = crud.get_invoices(db, user_id=user1.id)
        assert len(user1_invoices) == 2

    def test_update_invoice(self, db: Session):
        """Test updating an invoice."""
        # Create user and customer
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        created_invoice = crud.create_invoice(db, invoice_data, user.id)

        update_data = schemas.InvoiceUpdate(status=models.InvoiceStatus.SENT)
        updated_invoice = crud.update_invoice(db, created_invoice.id, update_data)

        assert updated_invoice is not None
        assert updated_invoice.status == models.InvoiceStatus.SENT

    def test_update_invoice_not_found(self, db: Session):
        """Test updating an invoice that doesn't exist."""
        update_data = schemas.InvoiceUpdate(status=models.InvoiceStatus.SENT)
        result = crud.update_invoice(db, "nonexistent-id", update_data)
        assert result is None

    def test_delete_invoice(self, db: Session):
        """Test deleting an invoice."""
        # Create user and customer
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        created_invoice = crud.create_invoice(db, invoice_data, user.id)

        result = crud.delete_invoice(db, created_invoice.id)
        assert result is True

        deleted_invoice = crud.get_invoice(db, created_invoice.id)
        assert deleted_invoice is None

    def test_delete_invoice_not_found(self, db: Session):
        """Test deleting an invoice that doesn't exist."""
        result = crud.delete_invoice(db, "nonexistent-id")
        assert result is False


class TestInvoiceItemCRUD:
    def test_create_invoice_item(self, db: Session):
        """Test creating an invoice item."""
        # Create user, customer, and invoice first
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id, status=models.InvoiceStatus.DRAFT, items=[]
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        # Create invoice item
        item_data = schemas.InvoiceItemCreate(
            description="Test Item", quantity=2, unit_price=50.0
        )
        item = crud.create_invoice_item(db, item_data, invoice.id)

        assert item.description == item_data.description
        assert item.quantity == item_data.quantity
        assert item.unit_price == item_data.unit_price
        assert item.total == 100.0  # 2 * 50.0
        assert item.invoice_id == invoice.id

    def test_update_invoice_item(self, db: Session):
        """Test updating an invoice item."""
        # Create user, customer, and invoice first
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)
        item = invoice.items[0]

        # Update the item
        update_data = schemas.InvoiceItemUpdate(quantity=3)
        updated_item = crud.update_invoice_item(db, item.id, update_data)

        assert updated_item is not None
        assert updated_item.quantity == 3

    def test_update_invoice_item_not_found(self, db: Session):
        """Test updating an invoice item that doesn't exist."""
        update_data = schemas.InvoiceItemUpdate(quantity=3)
        result = crud.update_invoice_item(db, "nonexistent-id", update_data)
        assert result is None

    def test_delete_invoice_item(self, db: Session):
        """Test deleting an invoice item."""
        # Create user, customer, and invoice first
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.DRAFT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)
        item = invoice.items[0]

        result = crud.delete_invoice_item(db, item.id)
        assert result is True

    def test_delete_invoice_item_not_found(self, db: Session):
        """Test deleting an invoice item that doesn't exist."""
        result = crud.delete_invoice_item(db, "nonexistent-id")
        assert result is False


class TestPaymentCRUD:
    def test_create_payment(self, db: Session):
        """Test creating a payment."""
        # Create user, customer, and invoice first
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.SENT,
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
            method=models.PaymentMethod.BANK_TRANSFER,
            status=models.PaymentStatus.PENDING,
        )
        payment = crud.create_payment(db, payment_data, user.id)

        assert payment.invoice_id == invoice.id
        assert payment.user_id == user.id
        assert payment.amount == payment_data.amount
        assert payment.method == payment_data.method
        assert payment.status == payment_data.status

    def test_get_payment(self, db: Session):
        """Test getting a payment by ID."""
        # Create user, customer, invoice, and payment
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.SENT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=models.PaymentMethod.BANK_TRANSFER,
            status=models.PaymentStatus.PENDING,
        )
        created_payment = crud.create_payment(db, payment_data, user.id)

        retrieved_payment = crud.get_payment(db, created_payment.id)
        assert retrieved_payment is not None
        assert retrieved_payment.id == created_payment.id

    def test_get_payment_not_found(self, db: Session):
        """Test getting a payment that doesn't exist."""
        payment = crud.get_payment(db, "nonexistent-id")
        assert payment is None

    def test_get_payments(self, db: Session):
        """Test getting payments with filters."""
        # Create users, customer, invoices, and payments
        user1_data = schemas.UserCreate(
            name="User 1",
            email="user1@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user1 = crud.create_user(db, user1_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        # Create invoices
        invoice1_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.SENT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item 1", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice1 = crud.create_invoice(db, invoice1_data, user1.id)

        invoice2_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.SENT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item 2", quantity=1, unit_price=200.0
                )
            ],
        )
        invoice2 = crud.create_invoice(db, invoice2_data, user1.id)

        # Create payments
        payment1_data = schemas.PaymentCreate(
            invoice_id=invoice1.id,
            amount=100.0,
            method=models.PaymentMethod.BANK_TRANSFER,
            status=models.PaymentStatus.PENDING,
        )
        crud.create_payment(db, payment1_data, user1.id)

        payment2_data = schemas.PaymentCreate(
            invoice_id=invoice2.id,
            amount=200.0,
            method=models.PaymentMethod.CREDIT_CARD,
            status=models.PaymentStatus.COMPLETED,
        )
        crud.create_payment(db, payment2_data, user1.id)

        # Get all payments
        all_payments = crud.get_payments(db)
        assert len(all_payments) == 2

        # Get payments by user
        user_payments = crud.get_payments(db, user_id=user1.id)
        assert len(user_payments) == 2

        # Get payments by invoice
        invoice_payments = crud.get_payments(db, invoice_id=invoice1.id)
        assert len(invoice_payments) == 1

    def test_update_payment(self, db: Session):
        """Test updating a payment."""
        # Create user, customer, invoice, and payment
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.SENT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=models.PaymentMethod.BANK_TRANSFER,
            status=models.PaymentStatus.PENDING,
        )
        created_payment = crud.create_payment(db, payment_data, user.id)

        # Update payment
        update_data = schemas.PaymentUpdate(status=models.PaymentStatus.COMPLETED)
        updated_payment = crud.update_payment(db, created_payment.id, update_data)

        assert updated_payment is not None
        assert updated_payment.status == models.PaymentStatus.COMPLETED

    def test_update_payment_not_found(self, db: Session):
        """Test updating a payment that doesn't exist."""
        update_data = schemas.PaymentUpdate(status=models.PaymentStatus.COMPLETED)
        result = crud.update_payment(db, "nonexistent-id", update_data)
        assert result is None

    def test_delete_payment(self, db: Session):
        """Test deleting a payment."""
        # Create user, customer, invoice, and payment
        user_data = schemas.UserCreate(
            name="Test User",
            email="user@example.com",
            password="testpassword",
            is_super_admin=False,
        )
        user = crud.create_user(db, user_data)

        customer_data = schemas.CustomerCreate(
            name="Test Customer",
            email="customer@example.com",
            phone="+1234567890",
            type=models.CustomerType.CUSTOMER,
        )
        customer = crud.create_customer(db, customer_data)

        invoice_data = schemas.InvoiceCreate(
            customer_id=customer.id,
            status=models.InvoiceStatus.SENT,
            items=[
                schemas.InvoiceItemCreate(
                    description="Test Item", quantity=1, unit_price=100.0
                )
            ],
        )
        invoice = crud.create_invoice(db, invoice_data, user.id)

        payment_data = schemas.PaymentCreate(
            invoice_id=invoice.id,
            amount=100.0,
            method=models.PaymentMethod.BANK_TRANSFER,
            status=models.PaymentStatus.PENDING,
        )
        created_payment = crud.create_payment(db, payment_data, user.id)

        result = crud.delete_payment(db, created_payment.id)
        assert result is True

        deleted_payment = crud.get_payment(db, created_payment.id)
        assert deleted_payment is None

    def test_delete_payment_not_found(self, db: Session):
        """Test deleting a payment that doesn't exist."""
        result = crud.delete_payment(db, "nonexistent-id")
        assert result is False
