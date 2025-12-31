from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(ge=0)
    stock_quantity: int = Field(ge=0)


class ProductCreate(ProductBase):
    id: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: str
    reserved_quantity: int
    available_quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int


# Inventory Schemas
class StockUpdateRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class ReservationResponse(BaseModel):
    id: int
    order_id: str
    product_id: str
    quantity: int
    is_released: bool
    created_at: datetime
    released_at: Optional[datetime] = None

    class Config:
        from_attributes = True
