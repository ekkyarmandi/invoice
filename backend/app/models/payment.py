from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
from .enums import PaymentMethod, PaymentStatus


class Payment(BaseModel):
    __tablename__ = "payments"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Relationships
    user = relationship("User", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

    def __str__(self) -> str:
        return f"Payment(${self.amount} - {self.method.value} - {self.status.value})"

    def __repr__(self) -> str:
        return f"<Payment(id='{self.id}', amount={self.amount}, method='{self.method.value}', status='{self.status.value}')>"
