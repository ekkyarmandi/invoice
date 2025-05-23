from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, auth, models
from ..database import get_db

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post(
    "/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED
)
def create_invoice(
    invoice: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Create a new invoice."""
    # Check if customer exists
    customer = crud.get_customer(db, customer_id=invoice.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    return crud.create_invoice(db=db, invoice=invoice, user_id=current_user.id)


@router.get("/", response_model=List[schemas.InvoiceResponse])
def read_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get all invoices."""
    # Super admins can see all invoices, regular users only their own
    user_id = None if current_user.is_super_admin else current_user.id
    invoices = crud.get_invoices(db, user_id=user_id, skip=skip, limit=limit)
    return invoices


@router.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
def read_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get a specific invoice."""
    db_invoice = crud.get_invoice(db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check if user has permission to view this invoice
    if not current_user.is_super_admin and db_invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return db_invoice


@router.put("/{invoice_id}", response_model=schemas.InvoiceResponse)
def update_invoice(
    invoice_id: str,
    invoice_update: schemas.InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Update an invoice."""
    db_invoice = crud.get_invoice(db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check if user has permission to update this invoice
    if not current_user.is_super_admin and db_invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Check if customer exists (if being updated)
    if invoice_update.customer_id is not None:
        customer = crud.get_customer(db, customer_id=invoice_update.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

    db_invoice = crud.update_invoice(
        db, invoice_id=invoice_id, invoice_update=invoice_update
    )
    return db_invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Delete an invoice."""
    db_invoice = crud.get_invoice(db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check if user has permission to delete this invoice
    if not current_user.is_super_admin and db_invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    success = crud.delete_invoice(db, invoice_id=invoice_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    # Return nothing for 204 No Content
    return


# Invoice Items endpoints
@router.post(
    "/{invoice_id}/items",
    response_model=schemas.InvoiceItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_item(
    invoice_id: str,
    item: schemas.InvoiceItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Add an item to an invoice."""
    db_invoice = crud.get_invoice(db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    # Check if user has permission to modify this invoice
    if not current_user.is_super_admin and db_invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return crud.create_invoice_item(db=db, item=item, invoice_id=invoice_id)


@router.put("/items/{item_id}", response_model=schemas.InvoiceItemResponse)
def update_invoice_item(
    item_id: str,
    item_update: schemas.InvoiceItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Update an invoice item."""
    # Get the item and its invoice
    db_item = (
        db.query(models.InvoiceItem).filter(models.InvoiceItem.id == item_id).first()
    )
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found"
        )

    db_invoice = crud.get_invoice(db, invoice_id=db_item.invoice_id)
    if not current_user.is_super_admin and db_invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    db_item = crud.update_invoice_item(db, item_id=item_id, item_update=item_update)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found"
        )
    return db_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Delete an invoice item."""
    # Get the item and its invoice
    db_item = (
        db.query(models.InvoiceItem).filter(models.InvoiceItem.id == item_id).first()
    )
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found"
        )

    db_invoice = crud.get_invoice(db, invoice_id=db_item.invoice_id)
    if not current_user.is_super_admin and db_invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    success = crud.delete_invoice_item(db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found"
        )
    # Return nothing for 204 No Content
    return
