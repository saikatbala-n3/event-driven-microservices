"""Event publisher instance."""

import sys
import os

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from shared.messaging import EventPublisher

# Global event publisher instance
event_publisher = EventPublisher(exchange_name="microservice.events")
