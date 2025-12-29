"""Common enumerations."""

from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class EventType(str, Enum):
    """Event type enumeration."""

    # Order events
    ORDER_CREATED = "order.created"
    ORDER_CONFIRMED = "order.confirmed"
    ORDER_CANCELLED = "order.cancelled"

    # Inventory events
    INVENTORY_RESERVED = "inventory.reserved"
    INVENTORY_RELEASED = "inventory.released"
    INVENTORY_INSUFFICIENT = "inventory.insufficient"

    # Payment events
    PAYMENT_PROCESSED = "payment.processed"
    PAYMENT_FAILED = "payment.failed"

    # Notification events (future)
    NOTIFICATION_SENT = "notification.sent"
