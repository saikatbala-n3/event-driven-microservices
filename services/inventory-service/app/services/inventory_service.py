from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.inventory import Product, InventoryReservation
from app.schemas.inventory import ProductCreate, ProductUpdate

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from shared.messaging.publisher import EventPublisher
from shared.models.items import InventoryItem
from shared.events.inventory_events import (
    InventoryReservedEvent,
    InventoryReleasedEvent,
    InventoryInsufficientEvent,
)

event_publisher = EventPublisher()


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_data: ProductCreate):
        """Create new product."""

        product = Product(
            id=product_data.id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
        )

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_product(self, product_id: str):
        """Get product by ID."""

        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def list_products(self, skip: int = 0, limit: int = 100):
        """Get list of products."""

        result = await self.db.execute(select(Product).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_product(self, product_id: str, product_data: ProductUpdate):
        """Update product details."""

        product = await self.get_product(product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        product.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def add_stock(self, product_id: str, quantity: int):
        """Add strock to a product."""

        product = await self.get_product(product_id)
        if not product:
            return None

        product.stock_quantity += quantity
        product.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def reserve_inventory(
        self,
        order_id: str,
        items: List[InventoryItem],
        total_amount: float,
        correlation_id: str,
    ):
        """
        Reserve inventory for an order with row-level locking to prevent race conditions.
        Returns True if successful, False if insufficient stock.
        Publishes InventoryReservedEvent or InventoryInsufficientEvent.
        """
        # Check if reservation already exists
        existing = await self.db.execute(
            select(InventoryReservation).where(
                InventoryReservation.order_id == order_id
            )
        )
        if existing.scalar_one_or_none():
            return True  # Already exists

        # Lock product rows and check availability atomically
        for item in items:
            result = await self.db.execute(
                select(Product)
                .where(Product.id == item.product_id)
                .with_for_update()  # Row-level lock to prevent concurrent modifications
            )
            product = result.scalar_one_or_none()

            if not product or product.available_quantity < item.quantity:
                # Insufficient stock - rollback and publish event
                await self.db.rollback()
                event = InventoryInsufficientEvent(
                    order_id=order_id,
                    unavailable_items=[
                        InventoryItem(
                            product_id=item.product_id, quantity=item.quantity
                        )
                    ],
                    correlation_id=correlation_id,
                )
                await event_publisher.publish_event(event)
                return False

            # Reserve stock (within locked transaction)
            product.reserved_quantity += item.quantity
            product.updated_at = datetime.now(timezone.utc)

            # Create reservation record
            reservation = InventoryReservation(
                order_id=order_id, product_id=item.product_id, quantity=item.quantity
            )
            self.db.add(reservation)

        # Commit transaction (releases locks)
        await self.db.commit()

        # Publish success event
        event = InventoryReservedEvent(
            order_id=order_id,
            items=[
                InventoryItem(product_id=item.product_id, quantity=item.quantity)
                for item in items
            ],
            total_amount=total_amount,
            correlation_id=correlation_id,
        )
        await event_publisher.publish_event(event)
        return True

    async def release_inventory(self, order_id: str, reason: str, correlation_id: str):
        """Release reserved inventory for cancelled order."""

        # Find all reservations for this order
        result = await self.db.execute(
            select(InventoryReservation).where(
                InventoryReservation.order_id == order_id,
                InventoryReservation.is_released == False,
            )
        )
        reservations = result.scalars().all()
        if not reservations:
            return

        # Release stock
        for reservation in reservations:
            product = await self.get_product(reservation.product_id)
            if product:
                product.reserved_quantity -= reservation.quantity
                product.updated_at = datetime.now(timezone.utc)

            reservation.is_released = True
            reservation.released_at = datetime.now(timezone.utc)

        await self.db.commit()

        # Publish event
        items = [
            InventoryItem(product_id=r.product_id, quantity=r.quantity)
            for r in reservations
        ]
        event = InventoryReleasedEvent(
            order_id=order_id, items=items, reason=reason, correlation_id=correlation_id
        )
        await event_publisher.publish_event(event)
