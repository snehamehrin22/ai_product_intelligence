"""Schema module for platform events and API models."""

from .events import (
    PlatformEvent,
    TaskCreatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
    PageViewedEvent,
    AgentMessageSentEvent,
    AgentMessageReceivedEvent,
    SessionStartedEvent,
)

__all__ = [
    "PlatformEvent",
    "TaskCreatedEvent",
    "TaskCompletedEvent",
    "TaskDeletedEvent",
    "TaskUpdatedEvent",
    "PageViewedEvent",
    "AgentMessageSentEvent",
    "AgentMessageReceivedEvent",
    "SessionStartedEvent",
]
