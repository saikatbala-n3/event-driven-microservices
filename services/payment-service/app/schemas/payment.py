from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from shared.models.enums import PaymentStatus


class PaymentCreate(BaseModel):
    order_id: str
    user_id: str
    amount: float = Field(gt=0)
    payment_created: str = "credit_card"


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: float
    status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
