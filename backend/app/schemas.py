from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import CustomerType, InvoiceStatus, PaymentMethod, PaymentStatus


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_super_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_super_admin: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    type: CustomerType = CustomerType.CUSTOMER


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    type: Optional[CustomerType] = None


class CustomerResponse(CustomerBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Invoice Item Schemas
class InvoiceItemBase(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None


class InvoiceItemResponse(InvoiceItemBase):
    id: str
    invoice_id: str
    total: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceBase(BaseModel):
    customer_id: str
    status: InvoiceStatus = InvoiceStatus.DRAFT


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = []


class InvoiceUpdate(BaseModel):
    customer_id: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    is_paid: Optional[bool] = None


class InvoiceResponse(InvoiceBase):
    id: str
    user_id: str
    date: datetime
    total_amount: float
    is_paid: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer: CustomerResponse
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentBase(BaseModel):
    invoice_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None


class PaymentResponse(PaymentBase):
    id: str
    user_id: str
    date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    invoice: Optional[InvoiceResponse] = None

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
