from .base import BaseEvent


# Notification Events
class NotificationSentEvent(BaseEvent):
    """Published when notification is successfully sent."""

    event_type: str = "notification.sent"
    notification_id: str
    order_id: str
    recipient: str
    channel: str  # email, sms, push
    subject: str


class NotificationFailedEvent(BaseEvent):
    """Published when notification sending fails."""

    event_type: str = "notification.failed"
    notification_id: str
    order_id: str
    recipient: str
    reason: str
