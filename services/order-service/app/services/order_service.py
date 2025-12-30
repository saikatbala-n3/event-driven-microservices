from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import sys
import os

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from shared.events import OrderCreatedEvent, OrderConfirmedEvent, OrderCancelledEvent
from shared.models.items import OrderItem as SharedOrderItem
from shared.models.enums import OrderStatus

from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate
from app.events.publisher import event_publisher


class OrderService:
    """Order service for business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order_data: OrderCreate):
        """Create a new order and publish OrderCreateEvent."""

        # Calculate total amount
        total_amount = sum(item.quantity * item.price for item in order_data.items)

        # Create order
        order = Order(
            id=str(uuid4()), user_id=order_data.user_id, total_amount=total_amount
        )

        for item_data in order_data.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price,
                # status=OrderStatus.PENDING,
            )
            order.items.append(order_item)

        # Save to database
        self.db.add(order)

        items_data = [
            SharedOrderItem(
                product_id=item.product_id, quantity=item.quantity, price=item.price
            )
            for item in order.items  # Access while in session
        ]

        await self.db.commit()
        await self.db.refresh(order, ["items"])

        # Publish OrderCreateEvent
        event = OrderCreatedEvent(
            order_id=order.id,
            user_id=order.user_id,
            items=items_data,
            total_amount=order.total_amount,
            correlation_id=order.id,
        )
        await event_publisher.publish_event(event)

        return order

    async def get_order(self, order_id: str):
        """Get order by ID."""

        result = await self.db.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def list_orders(
        self,
        user_id: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 0,
    ):
        """List orders with optional filters."""

        query = select(Order).options(selectinload(Order.items))

        if user_id:
            query = query.where(Order.user_id == user_id)
        if status:
            query = query.where(Order.status == status)

        query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def confirm_order(self, order_id: str):
        """Confirm an order."""

        order = await self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.now(timezone.utc)
        order.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(order, ["items"])

        # Publish OrderConfirmedEvent
        event = OrderConfirmedEvent(
            order_id=order_id, user_id=order.user_id, correlation_id=order.id
        )

        await event_publisher.publish_event(event)
        return order

    async def cancel_order(self, order_id: str, reason: str):
        """Cancel an order."""

        order = await self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.status = OrderStatus.CANCELLED
        order.confirmed_at = datetime.now(timezone.utc)
        order.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(order, ["items"])

        # Publish OrderCancelledEvent
        event = OrderCancelledEvent(
            order_id=order_id,
            user_id=order.user_id,
            reason=reason,
            correlation_id=order.id,
        )

        await event_publisher.publish_event(event)
        return order
