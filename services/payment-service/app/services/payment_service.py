from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.models.enums import PaymentStatus
from shared.messaging.publisher import EventPublisher
from shared.events.payment_events import PaymentFailedEvent, PaymentProcessedEvent

event_publisher = EventPublisher()


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payment_data: PaymentCreate):
        """Create new payment record."""

        payment = PaymentCreate(
            id=str(uuid4()),
            order_id=payment_data.order_id,
            user_id=payment_data.user_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            status=PaymentStatus.PENDING,
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_payment(self, payment_id: str):
        """Get payemnt by ID."""
        result = await self.db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def get_payment_by_order(self, order_id: str):
        """Get payemnt by ID."""
        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def process_payment(
        self, order_id: str, user_id: str, amount: float, correlation_id: str
    ):
        """
        Process payment for an order.
        Returns True if successful, False if failed.
        Publishes PaymentProcessedEvent or PaymentFailedEvent.
        """

        # Check if payment already exists
        existing = await self.get_payment_by_order(order_id)
        if existing:
            if existing.status == PaymentStatus.COMPLETED:
                return True  # Already processed
            if existing.status == PaymentStatus.FAILED:
                return False  # Already failed
            payment = existing
        else:
            # Create new payment record
            payment = Payment(
                id=str(uuid4()),
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status=PaymentStatus.PROCESSING,
            )
            self.db.add(payment)

        # Mock payment gateway call
        import random

        payment_successful = random.random() < 0.9
        if payment_successful:
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = f"txn_{uuid4().hex[:12]}"
            payment.processed_at = datetime.now(timezone.utc)

            await self.db.commit()
            await self.db.refresh(payment)

            # Publish payment success event
            event = PaymentProcessedEvent(
                order_id=order_id,
                payment_id=payment.id,
                amount=amount,
                transaction_id=payment.transaction_id,
                correlation_id=correlation_id,
                payment_method=payment.payment_method or "credit_card",
            )
            await event_publisher.publish_event(event)
            return True
        else:
            payment.status = PaymentStatus.FAILED
            payment.failed_at = datetime.now(timezone.utc)

            await self.db.commit()
            await self.db.refresh(payment)

            # Publish payment failed event
            event = PaymentFailedEvent(
                order_id=order_id,
                payment_id=payment.id,
                user_id=user_id,
                amount=amount,
                reason="Insufficient funds",
                correlation_id=correlation_id,
            )
            await event_publisher.publish_event(event)
            return False
