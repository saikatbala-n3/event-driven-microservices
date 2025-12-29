import logging
from typing import Optional
from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from ..events.base import BaseEvent
from .connection import get_rabbitmq_connection

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishing events to RabbitMQ."""

    def __init__(self, exchange_name: str = "microservice.events"):
        self.exchange_name = exchange_name
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractRobustChannel] = None
        self.exchange = None
        # self.exchange: Optional[AbstractExchange] = None

        # Event handlers: {EventType: [handler_functions]}
        # self.handlers: Dict[EventType, list[Callable]] = {}

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            # Create robust (auto-reconnecting) connection
            self.connection = await get_rabbitmq_connection()
            self.channel = await self.connection.channel()

            # Set QoS to process messages one at a time
            # Increase prefetch_count for higher throughput
            # await self.channel.set_qos(prefetch_count=10)

            # Declare topic exchange for events
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,  # Survive broker restart
            )

            logger.info("✓ Connected to RabbitMQ")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def publish_event(self, event: BaseEvent, routing_key: Optional[str] = None):
        """
        Publish event to exchange.

        Args:
            event: Event to publish
            routing_key: Routing key (defaults to event_type)
        """
        if not self.exchange:
            await self.connect()
            # raise RuntimeError("Not connected to RabbitMQ")

        routing_key = routing_key or event.event_type

        # Serialize event to JSON
        body = event.model_dump_json().encode()

        # Create persistent message
        message = Message(
            body=body,
            content_type="application/json",
            correlation_id=event.correlation_id,
            message_id=event.event_id,
            # timestamp=event.timestamp,
            # headers={
            #     "event_type": event.event_type.value,
            #     "causation_id": event.causation_id or "",
            # },
        )

        # Publish to exchange
        await self.exchange.publish(message, routing_key=routing_key)

        logger.info(
            f"Published: {event.event_type} "
            f"(ID: {event.event_id[:8]}..., routing_key: {routing_key})"
        )

    async def disconnect(self):
        """Close RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
