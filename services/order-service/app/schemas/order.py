from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import sys
import os

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from shared.models.enums import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating new order item."""

    product_id: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)


class OrderItemResponse(BaseModel):
    """Schema for order item response."""

    id: int
    product_id: str
    quantity: int
    price: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    user_id: str
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderResponse(BaseModel):
    """Schema for order response."""

    id: str
    user_id: str
    total_amount: float
    status: OrderStatus
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    confirned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for order list response."""

    orders: List[OrderResponse]
    total: int
