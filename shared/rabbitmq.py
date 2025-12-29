# shared/rabbitmq.py
"""
RabbitMQ client wrapper for event-driven communication.
Provides pub/sub functionality with automatic reconnection and error handling.
"""

import json
import logging
from typing import Optional, Callable, Dict

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractChannel,
    AbstractExchange,
)

from shared.events import BaseEvent, EventType, deserialize_event


logger = logging.getLogger(__name__)


class RabbitMQClient:
    """
    Async RabbitMQ client for event-driven communication.

    Features:
    - Automatic reconnection
    - Topic-based routing
    - Dead letter queue support
    - Message persistence
    - Event handler registration
    """

    def __init__(
        self, host: str, port: int, user: str, password: str, vhost: str = "/"
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost

        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange: Optional[AbstractExchange] = None

        # Event handlers: {EventType: [handler_functions]}
        self.handlers: Dict[EventType, list[Callable]] = {}

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            # Create robust (auto-reconnecting) connection
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                login=self.user,
                password=self.password,
                virtualhost=self.vhost,
            )

            self.channel = await self.connection.channel()

            # Set QoS to process messages one at a time
            # Increase prefetch_count for higher throughput
            await self.channel.set_qos(prefetch_count=10)

            # Declare topic exchange for events
            self.exchange = await self.channel.declare_exchange(
                "events",
                ExchangeType.TOPIC,
                durable=True,  # Survive broker restart
            )

            logger.info(f"✓ Connected to RabbitMQ at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        """Close RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            logger.info("✓ Disconnected from RabbitMQ")

    async def publish_event(self, event: BaseEvent, routing_key: Optional[str] = None):
        """
        Publish event to exchange.

        Args:
            event: Event to publish
            routing_key: Routing key (defaults to event_type)
        """
        if not self.exchange:
            raise RuntimeError("Not connected to RabbitMQ")

        routing_key = routing_key or event.event_type.value

        # Serialize event to JSON
        body = event.model_dump_json().encode()

        # Create persistent message
        message = Message(
            body=body,
            delivery_mode=DeliveryMode.PERSISTENT,  # Survive broker restart
            content_type="application/json",
            correlation_id=event.correlation_id,
            message_id=event.event_id,
            timestamp=event.timestamp,
            headers={
                "event_type": event.event_type.value,
                "causation_id": event.causation_id or "",
            },
        )

        # Publish to exchange
        await self.exchange.publish(message, routing_key=routing_key)

        logger.info(
            f"📤 Published: {event.event_type.value} "
            f"(ID: {event.event_id[:8]}..., routing_key: {routing_key})"
        )

    async def subscribe(
        self, queue_name: str, routing_keys: list[str], dlx_name: Optional[str] = None
    ):
        """
        Subscribe to events with specific routing keys.

        Args:
            queue_name: Queue name
            routing_keys: List of routing keys to bind (e.g., ["order.*", "inventory.reserved"])
            dlx_name: Dead letter exchange name (for failed messages)
        """
        if not self.channel or not self.exchange:
            raise RuntimeError("Not connected to RabbitMQ")

        # Declare dead letter exchange if specified
        if dlx_name:
            dlx = await self.channel.declare_exchange(
                dlx_name, ExchangeType.TOPIC, durable=True
            )

            # Declare dead letter queue
            dlq = await self.channel.declare_queue(f"{queue_name}.dlq", durable=True)

            # Bind DLQ to DLX with catch-all routing key
            await dlq.bind(dlx, routing_key="#")

            logger.info(f"✓ Created DLQ: {queue_name}.dlq")

        # Declare queue with optional DLX
        queue_arguments = {}
        if dlx_name:
            queue_arguments["x-dead-letter-exchange"] = dlx_name

        queue = await self.channel.declare_queue(
            queue_name, durable=True, arguments=queue_arguments
        )

        # Bind queue to exchange with routing keys
        for routing_key in routing_keys:
            await queue.bind(self.exchange, routing_key=routing_key)
            logger.info(f"✓ Bound {queue_name} to {routing_key}")

        # Start consuming messages
        await queue.consume(self._handle_message)

        logger.info(f"✓ Subscribed to queue: {queue_name}")

    def register_handler(self, event_type: EventType, handler: Callable):
        """
        Register event handler function.

        Args:
            event_type: Event type to handle
            handler: Async function to call when event received
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)
        logger.info(f"✓ Registered handler for: {event_type.value}")

    async def _handle_message(self, message: aio_pika.IncomingMessage):
        """
        Internal message handler.

        Args:
            message: Incoming RabbitMQ message
        """
        async with message.process(requeue=False):
            try:
                # Extract event type from headers
                event_type_str = message.headers.get("event_type")
                if not event_type_str:
                    logger.error("Missing event_type header, rejecting message")
                    return

                # Parse event
                event_data = json.loads(message.body.decode())
                event = deserialize_event(event_type_str, event_data)

                logger.info(
                    f"📥 Received: {event.event_type.value} "
                    f"(ID: {event.event_id[:8]}...)"
                )

                # Get registered handlers
                event_type = EventType(event_type_str)
                handlers = self.handlers.get(event_type, [])

                if not handlers:
                    logger.warning(f"No handlers registered for: {event_type.value}")
                    return

                # Call all registered handlers
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as handler_error:
                        logger.error(
                            f"Handler error for {event_type.value}: {handler_error}",
                            exc_info=True,
                        )
                        raise  # Re-raise to send to DLQ

                logger.info(f"✓ Processed: {event.event_type.value}")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                raise  # Message will be sent to DLQ if configured


# Global client instance
rabbitmq_client: Optional[RabbitMQClient] = None


async def init_rabbitmq(
    host: str, port: int, user: str, password: str, vhost: str = "/"
) -> RabbitMQClient:
    """
    Initialize global RabbitMQ client.

    Args:
        host: RabbitMQ host
        port: RabbitMQ port
        user: Username
        password: Password
        vhost: Virtual host

    Returns:
        RabbitMQ client instance
    """
    global rabbitmq_client

    rabbitmq_client = RabbitMQClient(host, port, user, password, vhost)
    await rabbitmq_client.connect()

    return rabbitmq_client


async def close_rabbitmq():
    """Close global RabbitMQ client."""
    if rabbitmq_client:
        await rabbitmq_client.disconnect()


def get_rabbitmq() -> RabbitMQClient:
    """
    Get global RabbitMQ client instance.

    Returns:
        RabbitMQ client

    Raises:
        RuntimeError: If client not initialized
    """
    if rabbitmq_client is None:
        raise RuntimeError(
            "RabbitMQ client not initialized. Call init_rabbitmq() first."
        )
    return rabbitmq_client
