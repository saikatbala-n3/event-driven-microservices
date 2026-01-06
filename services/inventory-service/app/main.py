import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.database import init_db, engine
from app.api.inventory import router as inventory_router
from app.events.consumer import start_consumers
from app.services.inventory_service import event_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await event_publisher.connect()
    asyncio.create_task(start_consumers())

    yield

    # Shutdown
    await event_publisher.close()
    await engine.dispose()


app = FastAPI(
    title="Inventory Service",
    description="Manages product inventory and reservations",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(inventory_router)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "inventory-service"}
