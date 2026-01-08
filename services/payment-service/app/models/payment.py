from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum
from app.database import Base

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from shared.models.enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    order_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(
        SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )

    # Payment gateway details
    transaction_id = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
