import logging
from typing import Optional, Callable
from aio_pika import ExchangeType
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel,
    AbstractIncomingMessage,
)
from .connection import get_rabbitmq_connection

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes events from RabbitMQ"""

    def __init__(
        self,
        queue_name: str,
        exchange_name: str = "microservice.events",
        routing_keys: list[str] = None,
    ):
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.routing_keys = routing_keys
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractRobustChannel] = None

    async def connect(self):
        """Establish connection with RabbitMQ"""
        try:
            # Create robust (auto-reconnecting) connection
            self.connection = await get_rabbitmq_connection()
            self.channel = await self.connection.channel()

            # Set QoS to process messages one at a time
            # Increase prefetch_count for higher throughput
            await self.channel.set_qos(prefetch_count=10)

            # Declare topic exchange for events
            exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,  # Survive broker restart
            )

            # Decalre queue
            queue = await self.channel.declare_queue(self.queue_name, durable=True)

            # Bind queue to exchange with routing key
            for routing_key in self.routing_keys:
                await queue.bind(exchange, routing_key=routing_key)

            return queue
            logger.info(f"✓ Connected to RabbitMQ at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def consume(self, callback: Callable):
        """Start consuming messages."""
        queue = await self.connect()

        async def on_message(message: AbstractIncomingMessage):
            async with message.process():
                await callback(message)

        await queue.consume(on_message)

    async def close(self):
        """Close the channel."""
        if self.channel:
            await self.channel.close()
