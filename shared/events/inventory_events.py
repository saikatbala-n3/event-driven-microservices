from typing import List
from .base import BaseEvent
from ..models.enums import EventType
from ..models.items import InventoryItem


# Inventory Events
class InventoryReservedEvent(BaseEvent):
    """Published when inventory is successfully reserved."""

    event_type: EventType = EventType.INVENTORY_RESERVED
    order_id: str
    items: List[InventoryItem]
    total_amount: float


class InventoryReleasedEvent(BaseEvent):
    """Published when inventory reservation is released (compensation)."""

    event_type: EventType = EventType.INVENTORY_RELEASED
    order_id: str
    reason: str


class InventoryInsufficientEvent(BaseEvent):
    """Published when inventory cannot be reserved."""

    event_type: EventType = EventType.INVENTORY_INSUFFICIENT
    order_id: str
    unavailable_items: List[InventoryItem]
