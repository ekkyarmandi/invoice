from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, auth, models
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED
)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Create a new payment."""
    # Check if invoice exists and user has permission
    invoice = crud.get_invoice(db, invoice_id=payment.invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check if user has permission to record payment for this invoice
    if not current_user.is_super_admin and invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return crud.create_payment(db=db, payment=payment, user_id=current_user.id)


@router.get("/", response_model=List[schemas.PaymentResponse])
def read_payments(
    invoice_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get all payments."""
    # Super admins can see all payments, regular users only their own
    user_id = None if current_user.is_super_admin else current_user.id
    payments = crud.get_payments(
        db, user_id=user_id, invoice_id=invoice_id, skip=skip, limit=limit
    )
    return payments


@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
def read_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get a specific payment."""
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    # Check if user has permission to view this payment
    if not current_user.is_super_admin and db_payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return db_payment


@router.put("/{payment_id}", response_model=schemas.PaymentResponse)
def update_payment(
    payment_id: str,
    payment_update: schemas.PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Update a payment."""
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    # Check if user has permission to update this payment
    if not current_user.is_super_admin and db_payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    db_payment = crud.update_payment(
        db, payment_id=payment_id, payment_update=payment_update
    )
    return db_payment


@router.delete("/{payment_id}")
def delete_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Delete a payment."""
    db_payment = crud.get_payment(db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    # Check if user has permission to delete this payment
    if not current_user.is_super_admin and db_payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    success = crud.delete_payment(db, payment_id=payment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )
    return {"message": "Payment deleted successfully"}
