from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from . import models, schemas
from .auth import get_password_hash


# User CRUD
def get_user(db: Session, user_id: str) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        is_super_admin=user.is_super_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: str, user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """Update user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    """Delete user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


# Customer CRUD
def get_customer(db: Session, customer_id: str) -> Optional[models.Customer]:
    """Get customer by ID."""
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customers(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Customer]:
    """Get all customers with pagination."""
    return db.query(models.Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    """Create new customer."""
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(
    db: Session, customer_id: str, customer_update: schemas.CustomerUpdate
) -> Optional[models.Customer]:
    """Update customer."""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None

    update_data = customer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: str) -> bool:
    """Delete customer."""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False

    db.delete(db_customer)
    db.commit()
    return True


# Invoice CRUD
def get_invoice(db: Session, invoice_id: str) -> Optional[models.Invoice]:
    """Get invoice by ID with related data."""
    return (
        db.query(models.Invoice)
        .options(
            joinedload(models.Invoice.customer),
            joinedload(models.Invoice.items),
            joinedload(models.Invoice.user),
        )
        .filter(models.Invoice.id == invoice_id)
        .first()
    )


def get_invoices(
    db: Session, user_id: Optional[str] = None, skip: int = 0, limit: int = 100
) -> List[models.Invoice]:
    """Get all invoices with pagination, optionally filtered by user."""
    query = db.query(models.Invoice).options(
        joinedload(models.Invoice.customer), joinedload(models.Invoice.items)
    )

    if user_id:
        query = query.filter(models.Invoice.user_id == user_id)

    return query.offset(skip).limit(limit).all()


def create_invoice(
    db: Session, invoice: schemas.InvoiceCreate, user_id: str
) -> models.Invoice:
    """Create new invoice with items."""
    # Calculate total amount
    total_amount = sum(item.quantity * item.unit_price for item in invoice.items)

    # Create invoice
    db_invoice = models.Invoice(
        user_id=user_id,
        customer_id=invoice.customer_id,
        status=invoice.status,
        total_amount=total_amount,
    )
    db.add(db_invoice)
    db.flush()  # Get the invoice ID

    # Create invoice items
    for item in invoice.items:
        item_total = item.quantity * item.unit_price
        db_item = models.InvoiceItem(
            invoice_id=db_invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total=item_total,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_invoice)
    return get_invoice(db, db_invoice.id)


def update_invoice(
    db: Session, invoice_id: str, invoice_update: schemas.InvoiceUpdate
) -> Optional[models.Invoice]:
    """Update invoice."""
    db_invoice = get_invoice(db, invoice_id)
    if not db_invoice:
        return None

    update_data = invoice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def delete_invoice(db: Session, invoice_id: str) -> bool:
    """Delete invoice."""
    db_invoice = get_invoice(db, invoice_id)
    if not db_invoice:
        return False

    db.delete(db_invoice)
    db.commit()
    return True


# Invoice Item CRUD
def create_invoice_item(
    db: Session, item: schemas.InvoiceItemCreate, invoice_id: str
) -> models.InvoiceItem:
    """Create new invoice item."""
    item_total = item.quantity * item.unit_price
    db_item = models.InvoiceItem(
        invoice_id=invoice_id,
        description=item.description,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total=item_total,
    )
    db.add(db_item)

    # Update invoice total
    invoice = get_invoice(db, invoice_id)
    if invoice:
        invoice.total_amount += item_total

    db.commit()
    db.refresh(db_item)
    return db_item


def update_invoice_item(
    db: Session, item_id: str, item_update: schemas.InvoiceItemUpdate
) -> Optional[models.InvoiceItem]:
    """Update invoice item."""
    db_item = (
        db.query(models.InvoiceItem).filter(models.InvoiceItem.id == item_id).first()
    )
    if not db_item:
        return None

    old_total = db_item.total
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    # Recalculate total
    db_item.total = db_item.quantity * db_item.unit_price

    # Update invoice total
    invoice = get_invoice(db, db_item.invoice_id)
    if invoice:
        invoice.total_amount = invoice.total_amount - old_total + db_item.total

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_invoice_item(db: Session, item_id: str) -> bool:
    """Delete invoice item."""
    db_item = (
        db.query(models.InvoiceItem).filter(models.InvoiceItem.id == item_id).first()
    )
    if not db_item:
        return False

    # Update invoice total
    invoice = get_invoice(db, db_item.invoice_id)
    if invoice:
        invoice.total_amount -= db_item.total

    db.delete(db_item)
    db.commit()
    return True


# Payment CRUD
def get_payment(db: Session, payment_id: str) -> Optional[models.Payment]:
    """Get payment by ID."""
    return (
        db.query(models.Payment)
        .options(joinedload(models.Payment.invoice))
        .filter(models.Payment.id == payment_id)
        .first()
    )


def get_payments(
    db: Session,
    user_id: Optional[str] = None,
    invoice_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Payment]:
    """Get all payments with pagination, optionally filtered by user or invoice."""
    query = db.query(models.Payment).options(joinedload(models.Payment.invoice))

    if user_id:
        query = query.filter(models.Payment.user_id == user_id)
    if invoice_id:
        query = query.filter(models.Payment.invoice_id == invoice_id)

    return query.offset(skip).limit(limit).all()


def create_payment(
    db: Session, payment: schemas.PaymentCreate, user_id: str
) -> models.Payment:
    """Create new payment."""
    db_payment = models.Payment(
        user_id=user_id,
        invoice_id=payment.invoice_id,
        amount=payment.amount,
        method=payment.method,
        status=payment.status,
    )
    db.add(db_payment)

    # Update invoice payment status if payment is completed
    if payment.status == models.PaymentStatus.COMPLETED:
        invoice = get_invoice(db, payment.invoice_id)
        if invoice:
            total_payments = sum(
                p.amount
                for p in invoice.payments
                if p.status == models.PaymentStatus.COMPLETED
            )
            total_payments += payment.amount

            if total_payments >= invoice.total_amount:
                invoice.is_paid = True
                invoice.status = models.InvoiceStatus.PAID

    db.commit()
    db.refresh(db_payment)
    return db_payment


def update_payment(
    db: Session, payment_id: str, payment_update: schemas.PaymentUpdate
) -> Optional[models.Payment]:
    """Update payment."""
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return None

    update_data = payment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_payment, field, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment


def delete_payment(db: Session, payment_id: str) -> bool:
    """Delete payment."""
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return False

    db.delete(db_payment)
    db.commit()
    return True
