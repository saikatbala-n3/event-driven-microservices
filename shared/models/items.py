"""Item models shared across services."""

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Represents an item in an order."""

    product_id: str
    quantity: int = Field(gt=0, description="Quantity must be positive")
    price: float = Field(ge=0, description="Price must be non-negative")

    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this item."""
        return self.quantity * self.price


class InventoryItem(BaseModel):
    """Represents an item for inventory operations."""

    product_id: str
    quantity: int = Field(gt=0, description="Quantity must be positive")
