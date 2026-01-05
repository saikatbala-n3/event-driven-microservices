from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.inventory import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    StockUpdateRequest,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Create a new product"""
    service = InventoryService(db)
    return await service.create_product(product)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Get product by ID"""
    service = InventoryService(db)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List all products"""
    service = InventoryService(db)
    products, total = await service.list_products(skip, limit)
    return ProductListResponse(products=products, total=total)


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str, product_update: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    """Update product details"""
    service = InventoryService(db)
    product = await service.update_product(product_id, product_update)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products/{product_id}/stock", response_model=ProductResponse)
async def add_stock(
    product_id: str,
    stock_update: StockUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add stock to a product"""
    service = InventoryService(db)
    product = await service.add_stock(product_id, stock_update.quantity)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
