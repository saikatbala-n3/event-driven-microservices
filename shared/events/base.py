from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """
    Base event schema following CloudEvents spec.

    All events must include:
    - event_id: Unique identifier
    - event_type: Type of event
    - timestamp: When event occurred
    - correlation_id: For distributed tracing
    - causation_id: Which event caused this (optional)
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
