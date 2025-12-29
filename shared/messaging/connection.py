import os
from typing import Optional
import aio_pika
from aio_pika.abc import AbstractRobustConnection

_connection: Optional[AbstractRobustConnection] = None


async def get_rabbitmq_connection():
    """Get or create RabbitMQ connection."""
    global _connection

    if _connection is None or _connection.is_closed:
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
        _connection = await aio_pika.connect_robust(rabbitmq_url)

    return _connection


async def close_rabbitmq_connection():
    """Close RabbitMQ connection."""
    global _connection

    if _connection and not _connection.is_closed:
        await _connection.close()
        _connection = None
