from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_super_admin = Column(Boolean, default=False)

    # Relationships
    invoices = relationship("Invoice", back_populates="user")
    payments = relationship("Payment", back_populates="user")

    def __str__(self) -> str:
        return f"User({self.name} - {self.email})"

    def __repr__(self) -> str:
        return f"<User(id='{self.id}', name='{self.name}', email='{self.email}', is_super_admin={self.is_super_admin})>"
