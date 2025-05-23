from sqlalchemy import (
    Boolean,
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
from .enums import InvoiceStatus


class Invoice(BaseModel):
    __tablename__ = "invoices"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    total_amount = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    payments = relationship("Payment", back_populates="invoice")

    def __str__(self) -> str:
        return f"Invoice({self.id} - {self.status.value} - ${self.total_amount})"

    def __repr__(self) -> str:
        return f"<Invoice(id='{self.id}', status='{self.status.value}', total_amount={self.total_amount}, is_paid={self.is_paid})>"


class InvoiceItem(BaseModel):
    __tablename__ = "invoice_items"

    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

    def __str__(self) -> str:
        return f"InvoiceItem({self.description} - Qty: {self.quantity} - ${self.total})"

    def __repr__(self) -> str:
        return f"<InvoiceItem(id='{self.id}', description='{self.description}', quantity={self.quantity}, total={self.total})>"
