"""Event schemas for microservices communication."""

from .base import BaseEvent
from .order_events import OrderCreatedEvent, OrderCancelledEvent, OrderConfirmedEvent
from .inventory_events import InventoryReservedEvent, InventoryReleasedEvent
from .payment_events import PaymentProcessedEvent, PaymentFailedEvent

__all__ = [
    "BaseEvent",
    "OrderCreatedEvent",
    "OrderConfirmedEvent",
    "OrderCancelledEvent",
    "InventoryReservedEvent",
    "InventoryReleasedEvent",
    "PaymentProcessedEvent",
    "PaymentFailedEvent",
]
