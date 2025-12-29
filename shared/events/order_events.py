from typing import List
from .base import BaseEvent
from ..models.enums import EventType
from ..models.items import OrderItem


class OrderCreatedEvent(BaseEvent):
    """Published when a new order is created."""

    event_type: EventType = EventType.ORDER_CREATED
    order_id: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    # currency: str = "USD"


class OrderConfirmedEvent(BaseEvent):
    """Published when order is successfully completed."""

    event_type: EventType = EventType.ORDER_CONFIRMED
    order_id: str
    user_id: str
    # completed_at: datetime = Field(default_factory=datetime.now(UTC))


class OrderCancelledEvent(BaseEvent):
    """Published when order is cancelled."""

    event_type: EventType = EventType.ORDER_CANCELLED
    order_id: str
    user_id: str
    reason: str
    # cancelled_at: datetime = Field(default_factory=datetime.now(UTC))


# class OrderFailedEvent(BaseEvent):
#     """Published when order processing fails."""

#     event_type: EventType = EventType.ORDER_FAILED
#     order_id: str
#     user_id: str
#     reason: str
#     # failed_at: datetime = Field(default_factory=datetime.now(UTC))
