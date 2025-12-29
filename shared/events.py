from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from pydantic import BaseModel, Field
import uuid


class EventType(str, Enum):
    """Event types in the system."""

    # Order events
    ORDER_CREATED = "order.created"
    ORDER_VALIDATED = "order.validated"
    ORDER_COMPLETED = "order.completed"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_FAILED = "order.failed"

    # Inventory events
    INVENTORY_RESERVED = "inventory.reserved"
    INVENTORY_RELEASED = "inventory.released"
    INVENTORY_INSUFFICIENT = "inventory.insufficient"

    # Payment events
    PAYMENT_PROCESSED = "payment.processed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"

    # Notification events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"


# Order Events
class OrderItem(BaseModel):
    """Order item schema."""

    product_id: str
    product_name: str
    quantity: int
    unit_price: float


# Event Registry for deserialization
EVENT_REGISTRY = {
    EventType.ORDER_CREATED: OrderCreatedEvent,
    EventType.ORDER_COMPLETED: OrderCompletedEvent,
    EventType.ORDER_CANCELLED: OrderCancelledEvent,
    EventType.ORDER_FAILED: OrderFailedEvent,
    EventType.INVENTORY_RESERVED: InventoryReservedEvent,
    EventType.INVENTORY_RELEASED: InventoryReleasedEvent,
    EventType.INVENTORY_INSUFFICIENT: InventoryInsufficientEvent,
    EventType.PAYMENT_PROCESSED: PaymentProcessedEvent,
    EventType.PAYMENT_FAILED: PaymentFailedEvent,
    EventType.PAYMENT_REFUNDED: PaymentRefundedEvent,
    EventType.NOTIFICATION_SENT: NotificationSentEvent,
    EventType.NOTIFICATION_FAILED: NotificationFailedEvent,
}


def deserialize_event(event_type_str: str, data: dict) -> BaseEvent:
    """
    Deserialize event from dictionary.

    Args:
        event_type_str: Event type as string
        data: Event data dictionary

    Returns:
        Event instance

    Raises:
        ValueError: If event type is unknown
    """
    try:
        event_type = EventType(event_type_str)
    except ValueError:
        raise ValueError(f"Unknown event type: {event_type_str}")

    event_class = EVENT_REGISTRY.get(event_type)
    if not event_class:
        raise ValueError(f"No schema registered for event type: {event_type_str}")

    return event_class(**data)
