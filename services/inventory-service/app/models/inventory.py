from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    @property
    def available_quantity(self):
        """Calculate available stock (total - reserved)."""
        return self.stock_quantity - self.reserved_quantity


class InventoryReservation(Base):
    __tablename__ = "Inventory_reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    is_released = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    released_at = Column(DateTime(timezone=True), nullable=True)
