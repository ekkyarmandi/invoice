from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from .enums import CustomerType


class Customer(BaseModel):
    __tablename__ = "customers"

    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    type = Column(Enum(CustomerType), nullable=False, default=CustomerType.CUSTOMER)

    # Relationships
    invoices = relationship("Invoice", back_populates="customer")

    def __str__(self) -> str:
        return f"Customer({self.name} - {self.type.value})"

    def __repr__(self) -> str:
        return f"<Customer(id='{self.id}', name='{self.name}', email='{self.email}', type='{self.type.value}')>"
