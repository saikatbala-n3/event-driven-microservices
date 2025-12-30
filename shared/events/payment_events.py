from typing import Optional
from .base import BaseEvent
from shared.models.enums import EventType


# Payment Events
class PaymentProcessedEvent(BaseEvent):
    """Published when payment is successfully processed."""

    event_type: EventType = EventType.PAYMENT_PROCESSED
    order_id: str
    amount: float
    payment_id: str
    transaction_id: str
    payment_method: Optional[str] = "credict_card"


class PaymentFailedEvent(BaseEvent):
    """Published when payment processing fails."""

    event_type: EventType = EventType.PAYMENT_FAILED
    reason: str
    user_id: str
    order_id: str
    amount: float
    payment_id: str


# class PaymentRefundedEvent(BaseEvent):
#     """Published when payment is refunded (compensation)."""

#     event_type: EventType = EventType.PAYMENT_REFUNDED
#     order_id: str
#     payment_id: str
#     refund_amount: float
#     reason: str
