from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.db.session import Base

# import sys
# import os

from shared.models.enums import OrderStatus


class Order(Base):
    """Order model."""

    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    status = Column(
        SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True
    )
    total_amount = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda x: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda x: datetime.now(timezone.utc),
        onupdate=lambda x: datetime.now(timezone.utc),
        nullable=False,
    )
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"


class OrderItem(Base):
    """Order item model."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")

    @property
    def subtotal(self) -> float:
        """Calculate subtotal."""
        return self.quantity * self.price

    def __repr__(self):
        return f"<OrderItem(product_id={self.product_id}, quantity={self.quantity})>"
