import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
from aio_pika import IncomingMessage as AbstractIncomingMessage

from shared.messaging.consumer import EventConsumer
from shared.models.enums import EventType
from shared.models.items import InventoryItem
from app.database import async_session
from app.services.inventory_service import InventoryService


async def handle_order_created(message: AbstractIncomingMessage):
    """Handle OrderCreated event - reserve inventory"""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")
        items_data = event_data.get("items", [])
        correlation_id = event_data.get("correlation_id")
        total_amount = event_data.get("total_amount")

        # Convert to InventoryItem models
        items = [InventoryItem(**item) for item in items_data]

        # Reserve inventory
        async with async_session() as db:
            service = InventoryService(db)
            await service.reserve_inventory(
                order_id, items, total_amount, correlation_id
            )

    except Exception as e:
        print(f"[Inventory Service] Error handling order_created: {e}")


async def handle_order_cancelled(message: AbstractIncomingMessage):
    """Handle OrderCancelled event - release inventory"""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")
        reason = event_data.get("reason", "Order cancelled")
        correlation_id = event_data.get("correlation_id")

        # Release inventory
        async with async_session() as db:
            service = InventoryService(db)
            await service.release_inventory(order_id, reason, correlation_id)

    except Exception as e:
        print(f"[Inventory Service] Error handling order_cancelled: {e}")


async def start_consumers():
    """Start all event consumers"""
    order_consumer = EventConsumer(
        queue_name="inventory_service.orders",
        routing_keys=[EventType.ORDER_CREATED, EventType.ORDER_CANCELLED],
    )

    async def order_router(message: AbstractIncomingMessage):
        event_data = json.loads(message.body.decode())
        event_type = event_data.get("event_type")

        if event_type == EventType.ORDER_CREATED:
            await handle_order_created(message)
        elif event_type == EventType.ORDER_CANCELLED:
            await handle_order_cancelled(message)

    await order_consumer.consume(order_router)
    print("[Inventory Service] Event consumers started")
