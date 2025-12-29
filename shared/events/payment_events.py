from .base import BaseEvent


# Payment Events
class PaymentProcessedEvent(BaseEvent):
    """Published when payment is successfully processed."""

    event_type: str = "payment.processed"
    order_id: str
    payment_id: str
    amount: float
    # currency: str = "USD"
    payment_method: str
    payment_id: str


class PaymentFailedEvent(BaseEvent):
    """Published when payment processing fails."""

    event_type: str = "payment.failed"
    order_id: str
    user_id: str
    reason: str
    amount: float


# class PaymentRefundedEvent(BaseEvent):
#     """Published when payment is refunded (compensation)."""

#     event_type: EventType = EventType.PAYMENT_REFUNDED
#     order_id: str
#     payment_id: str
#     refund_amount: float
#     reason: str
