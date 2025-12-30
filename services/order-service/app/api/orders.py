from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from shared.models.enums import OrderStatus

from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new order."""

    order_service = OrderService(db)
    order = await order_service.create_order(order_data)
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get order by ID."""

    order_service = OrderService(db)
    order = await order_service.get_order(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.get("", response_model=OrderListResponse)
async def list_orders(
    user_id: Optional[str] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List orders with optional filters."""

    order_service = OrderService(db)
    orders = await order_service.list_orders(
        user_id=user_id, status=status, skip=skip, limit=limit
    )

    return OrderListResponse(orders=orders, total=len(orders))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    reason: str = Query(..., description="Reason for cancellation"),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an order."""

    order_service = OrderService(db)

    try:
        order = await order_service.cancel_order(order_id, reason)
        return order
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
