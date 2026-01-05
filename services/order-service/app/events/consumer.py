import os
import sys
import json
from aio_pika.abc import AbstractIncomingMessage

from app.db.session import async_session
from app.services.order_service import OrderService

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from shared.messaging import EventConsumer
from shared.models.enums import EventType


async def handle_inventory_reserved(message: AbstractIncomingMessage):
    """Handle InventoryReservedEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")

        print(f"[Order Service] Inventory reserved for order {order_id}")

        # Delegate to service layer
        async with async_session() as db:
            service = OrderService(db)
            await service.update_to_processing(order_id)

    except Exception as e:
        print(f"[Order Service] Error handling inventory_reserved: {e}")


async def handle_inventory_insufficient(message: AbstractIncomingMessage):
    """Handle InventoryInsufficientEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")
        correlation_id = event_data.get("correlation_id")

        print(f"[Order Service] Insufficient inventory for order {order_id}")

        # Delegate to service layer
        async with async_session() as db:
            service = OrderService(db)
            await service.cancel_order(
                order_id=order_id,
                reason="Insufficient inventory",
                correlation_id=correlation_id,
            )

    except Exception as e:
        print(f"[Order Service] Error handling inventory_insufficient: {e}")


async def handle_payment_processed(message: AbstractIncomingMessage):
    """Handle PaymentProcessedEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")

        print(f"[Order Service] Payment processed for order {order_id}")

        # Delegate to service layer
        async with async_session() as db:
            service = OrderService(db)
            await service.confirm_order(order_id)

    except Exception as e:
        print(f"[Order Service] Error handling payment_processed: {e}")


async def handle_payment_failed(message: AbstractIncomingMessage):
    """Handle PaymentFailedEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")
        reason = event_data.get("reason", "Payment failed")
        correlation_id = event_data.get("correlation_id")

        print(f"[Order Service] Payment failed for order {order_id}: {reason}")

        # Delegate to service layer
        async with async_session() as db:
            service = OrderService(db)
            await service.cancel_order(
                order_id=order_id, reason=reason, correlation_id=correlation_id
            )

    except Exception as e:
        print(f"[Order Service] Error handling payment_failed: {e}")


async def start_consumers():
    """Start all event consumers."""

    # Consumer for inventory events
    inventory_consumer = EventConsumer(
        queue_name="order_service.inventory",
        routing_keys=[
            EventType.INVENTORY_RESERVED,
            EventType.INVENTORY_INSUFFICIENT,  # Added!
        ],
    )

    # Consumer for payment events
    payment_consumer = EventConsumer(
        queue_name="order_service.payment",
        routing_keys=[EventType.PAYMENT_PROCESSED, EventType.PAYMENT_FAILED],
    )

    # Route inventory events
    async def inventory_router(message: AbstractIncomingMessage):
        event_data = json.loads(message.body.decode())
        event_type = event_data.get("event_type")

        if event_type == EventType.INVENTORY_RESERVED:
            await handle_inventory_reserved(message)
        elif event_type == EventType.INVENTORY_INSUFFICIENT:
            await handle_inventory_insufficient(message)

    # Route payment events
    async def payment_router(message: AbstractIncomingMessage):
        event_data = json.loads(message.body.decode())
        event_type = event_data.get("event_type")

        if event_type == EventType.PAYMENT_PROCESSED:
            await handle_payment_processed(message)
        elif event_type == EventType.PAYMENT_FAILED:
            await handle_payment_failed(message)

    await inventory_consumer.consume(inventory_router)
    await payment_consumer.consume(payment_router)

    print("[Order Service] Event consumers started")
