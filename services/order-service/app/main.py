import asyncio
import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app

from app.config import settings
from app.db.session import init_db, engine
from app.api import orders_router
from app.events import start_consumers
from app.services.order_service import event_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"[{settings.SERVICE_NAME}] Starting up...")

    # Initialize database
    await init_db()
    print(f"[{settings.SERVICE_NAME}] Database initialized")

    # Connect event publisher
    await event_publisher.connect()
    print(f"[{settings.SERVICE_NAME}] Event publisher connected")

    # Start event consumers in background
    asyncio.create_task(start_consumers())

    yield

    # Shutdown
    print(f"[{settings.SERVICE_NAME}] Shutting down...")
    await event_publisher.close()
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Order Service",
    description="Microservice for handling orders",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(orders_router)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"service": settings.SERVICE_NAME, "version": "0.1.0", "status": "running"}
