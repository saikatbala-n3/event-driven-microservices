import os
import sys
import json
from sqlalchemy import select
from datetime import datetime, timezone
from aio_pika.abc import AbstractIncomingMessage

from app.db.session import async_session
from app.models.order import Order

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from shared.messaging import EventConsumer
from shared.models.enums import EventType
from shared.models.enums import OrderStatus


async def handle_inventory_reserved(message: AbstractIncomingMessage):
    """Handle InventoryReservedEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")

        print(f"[Order Service] Inventory reserved for order {order_id}")

        # Update order status directly
        async with async_session() as db:
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()

            if order:
                order.status = OrderStatus.PROCESSING
                order.updated_at = datetime.now(timezone.utc)
                await db.commit()
                print(f"[Order Service] Order {order_id} status updated to PROCESSING")

    except Exception as e:
        print(f"[Order Service] Error handling inventory_reserved: {e}")


async def handle_payment_processed(message: AbstractIncomingMessage):
    """Handle PaymentProcessedEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")

        print(f"[Order Service] Payment processed for order {order_id}")

        # Confirm the order directly
        async with async_session() as db:
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()

            if order:
                order.status = OrderStatus.CONFIRMED
                order.confirmed_at = datetime.now(timezone.utc)
                order.updated_at = datetime.now(timezone.utc)
                await db.commit()
                print(f"[Order Service] Order {order_id} confirmed")

    except Exception as e:
        print(f"[Order Service] Error handling payment_processed: {e}")


async def handle_payment_failed(message: AbstractIncomingMessage):
    """Handle PaymentFailedEvent."""
    try:
        event_data = json.loads(message.body.decode())
        order_id = event_data.get("order_id")
        reason = event_data.get("reason", "Payment failed")

        print(f"[Order Service] Payment failed for order {order_id}: {reason}")

        # Cancel the order directly
        async with async_session() as db:
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()

            if order:
                order.status = OrderStatus.CANCELLED
                order.cancelled_at = datetime.now(timezone.utc)
                order.updated_at = datetime.now(timezone.utc)
                await db.commit()
                print(
                    f"[Order Service] Order {order_id} cancelled due to payment failure"
                )

    except Exception as e:
        print(f"[Order Service] Error handling payment_failed: {e}")


async def start_consumers():
    """Start all event consumers."""

    # Consumer for inventory events
    inventory_consumer = EventConsumer(
        queue_name="order_service.inventory",
        routing_keys=[EventType.INVENTORY_RESERVED],
    )

    # Consumer for payment events
    payment_consumer = EventConsumer(
        queue_name="order_service.payment",
        routing_keys=[EventType.PAYMENT_PROCESSED, EventType.PAYMENT_FAILED],
    )

    # Consumer for payment events
    await inventory_consumer.consume(handle_inventory_reserved)

    # Route payment events to appropriate handlers
    async def payment_router(message: AbstractIncomingMessage):
        event_data = json.loads(message.body.decode())
        event_type = event_data.get("event_type")

        if event_type == EventType.PAYMENT_PROCESSED:
            await handle_payment_processed(message)
        elif event_type == EventType.PAYMENT_FAILED:
            await handle_payment_failed(message)

    await payment_consumer.consume(payment_router)

    print("[Order Service] Event consumers started")
