"""Platform Event Schemas.

Pydantic models for all platform events published to Databricks Delta Lake via Zerobus.

Event Types:
- task_created: User creates a new task
- task_completed: User marks a task as completed
- task_deleted: User deletes a task
- task_updated: User updates task fields
- page_viewed: User navigates to a page
- agent_message_sent: User sends message to AI agent
- agent_message_received: AI agent responds to user
- session_started: User session begins

Schema Evolution:
- All events have 'event_version' field (default "v1")
- New fields can be added without breaking existing consumers
- Delta Lake automatically handles schema evolution
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class PlatformEvent(BaseModel):
    """
    Base schema for all platform events.

    Common Fields:
    - event_id: Unique identifier (UUID v4)
    - event_name: Event type (e.g., 'task_created')
    - event_version: Schema version for evolution (default 'v1')
    - timestamp: Event occurrence time (ISO8601 with timezone)
    - session_id: User session identifier (join key for analysis)
    - user_id: User identifier
    - properties: Event-specific data (flexible dict)

    Example:
        {
            "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "event_name": "task_created",
            "event_version": "v1",
            "timestamp": "2024-01-15T10:30:00.000Z",
            "session_id": "abc-123-session",
            "user_id": "user-456",
            "properties": {"task_id": "task-789", "title": "Buy milk"}
        }
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier (UUID v4)",
    )
    event_name: str = Field(..., description="Event type identifier")
    event_version: str = Field(
        default="v1",
        description="Schema version for evolution (e.g., v1, v2)",
        pattern=r"^v\d+$",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Event occurrence time (ISO8601 with timezone)",
    )
    session_id: str = Field(
        ...,
        description="User session identifier (join key with agent traces)",
        min_length=1,
    )
    user_id: str = Field(..., description="User identifier", min_length=1)
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Event-specific data (flexible dict)"
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is valid ISO8601 format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                f"Invalid timestamp format: {v}. Expected ISO8601 (e.g., 2024-01-15T10:30:00.000Z)"
            )
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "event_name": "task_created",
                "event_version": "v1",
                "timestamp": "2024-01-15T10:30:00.000Z",
                "session_id": "abc-123-session",
                "user_id": "user-456",
                "properties": {"task_id": "task-789", "title": "Buy milk"},
            }
        }


# ============================================================================
# Task Events
# ============================================================================


class TaskCreatedEvent(PlatformEvent):
    """
    Event emitted when a user creates a new task.

    Properties:
    - task_id (str): Unique task identifier
    - title (str): Task title
    - description (str, optional): Task description
    - status (str): Initial task status (usually 'pending')
    - priority (str, optional): Task priority level
    - due_date (str, optional): Task due date (ISO8601)

    Example:
        {
            "event_name": "task_created",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "task_id": "task-789",
                "title": "Buy milk",
                "description": "Get 2% milk from store",
                "status": "pending",
                "priority": "high",
                "due_date": "2024-01-16T18:00:00Z"
            }
        }
    """

    event_name: Literal["task_created"] = "task_created"

    @field_validator("properties")
    @classmethod
    def validate_task_created_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required properties for task_created event."""
        required_fields = ["task_id", "title", "status"]
        missing = [f for f in required_fields if f not in v]
        if missing:
            raise ValueError(
                f"Missing required properties for task_created: {', '.join(missing)}"
            )
        return v


class TaskCompletedEvent(PlatformEvent):
    """
    Event emitted when a user marks a task as completed.

    Properties:
    - task_id (str): Unique task identifier
    - title (str): Task title
    - completed_at (str): Completion timestamp (ISO8601)
    - time_to_complete_seconds (int, optional): Time from creation to completion

    Example:
        {
            "event_name": "task_completed",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "task_id": "task-789",
                "title": "Buy milk",
                "completed_at": "2024-01-15T11:00:00Z",
                "time_to_complete_seconds": 1800
            }
        }
    """

    event_name: Literal["task_completed"] = "task_completed"

    @field_validator("properties")
    @classmethod
    def validate_task_completed_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required properties for task_completed event."""
        required_fields = ["task_id", "title", "completed_at"]
        missing = [f for f in required_fields if f not in v]
        if missing:
            raise ValueError(
                f"Missing required properties for task_completed: {', '.join(missing)}"
            )
        return v


class TaskDeletedEvent(PlatformEvent):
    """
    Event emitted when a user deletes a task.

    Properties:
    - task_id (str): Unique task identifier
    - title (str): Task title
    - status (str): Task status at deletion time

    Example:
        {
            "event_name": "task_deleted",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "task_id": "task-789",
                "title": "Buy milk",
                "status": "pending"
            }
        }
    """

    event_name: Literal["task_deleted"] = "task_deleted"

    @field_validator("properties")
    @classmethod
    def validate_task_deleted_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required properties for task_deleted event."""
        required_fields = ["task_id", "title", "status"]
        missing = [f for f in required_fields if f not in v]
        if missing:
            raise ValueError(
                f"Missing required properties for task_deleted: {', '.join(missing)}"
            )
        return v


class TaskUpdatedEvent(PlatformEvent):
    """
    Event emitted when a user updates task fields.

    Properties:
    - task_id (str): Unique task identifier
    - title (str): Current task title
    - updated_fields (list[str]): Names of fields that were updated
    - previous_values (dict, optional): Previous values of updated fields
    - current_values (dict): Current values of updated fields

    Example:
        {
            "event_name": "task_updated",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "task_id": "task-789",
                "title": "Buy milk",
                "updated_fields": ["priority", "due_date"],
                "previous_values": {"priority": "low", "due_date": null},
                "current_values": {"priority": "high", "due_date": "2024-01-16T18:00:00Z"}
            }
        }
    """

    event_name: Literal["task_updated"] = "task_updated"

    @field_validator("properties")
    @classmethod
    def validate_task_updated_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required properties for task_updated event."""
        required_fields = ["task_id", "title", "updated_fields", "current_values"]
        missing = [f for f in required_fields if f not in v]
        if missing:
            raise ValueError(
                f"Missing required properties for task_updated: {', '.join(missing)}"
            )
        return v


# ============================================================================
# Navigation Events
# ============================================================================


class PageViewedEvent(PlatformEvent):
    """
    Event emitted when a user navigates to a page.

    Properties:
    - page_path (str): URL path or route (e.g., '/tasks', '/agent')
    - page_title (str, optional): Page title
    - referrer (str, optional): Previous page URL

    Example:
        {
            "event_name": "page_viewed",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "page_path": "/tasks",
                "page_title": "My Tasks",
                "referrer": "/dashboard"
            }
        }
    """

    event_name: Literal["page_viewed"] = "page_viewed"

    @field_validator("properties")
    @classmethod
    def validate_page_viewed_properties(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required properties for page_viewed event."""
        if "page_path" not in v:
            raise ValueError("Missing required property 'page_path' for page_viewed")
        return v


# ============================================================================
# Agent Interaction Events
# ============================================================================


class AgentMessageSentEvent(PlatformEvent):
    """
    Event emitted when a user sends a message to the AI agent.

    Properties:
    - message_id (str): Unique message identifier
    - message_text (str): User's message content
    - message_length (int): Character count
    - conversation_id (str, optional): Conversation thread identifier

    Example:
        {
            "event_name": "agent_message_sent",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "message_id": "msg-001",
                "message_text": "Create a task to buy milk tomorrow",
                "message_length": 37,
                "conversation_id": "conv-789"
            }
        }
    """

    event_name: Literal["agent_message_sent"] = "agent_message_sent"

    @field_validator("properties")
    @classmethod
    def validate_agent_message_sent_properties(
        cls, v: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate required properties for agent_message_sent event."""
        required_fields = ["message_id", "message_text"]
        missing = [f for f in required_fields if f not in v]
        if missing:
            raise ValueError(
                f"Missing required properties for agent_message_sent: {', '.join(missing)}"
            )
        return v


class AgentMessageReceivedEvent(PlatformEvent):
    """
    Event emitted when the AI agent responds to a user message.

    Properties:
    - message_id (str): Unique message identifier
    - response_text (str): Agent's response content
    - response_length (int): Character count
    - conversation_id (str, optional): Conversation thread identifier
    - user_message_id (str, optional): ID of user message being responded to
    - response_time_ms (int, optional): Time to generate response in milliseconds

    Example:
        {
            "event_name": "agent_message_received",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "message_id": "msg-002",
                "response_text": "I've created a task 'Buy milk' with due date tomorrow.",
                "response_length": 59,
                "conversation_id": "conv-789",
                "user_message_id": "msg-001",
                "response_time_ms": 1250
            }
        }
    """

    event_name: Literal["agent_message_received"] = "agent_message_received"

    @field_validator("properties")
    @classmethod
    def validate_agent_message_received_properties(
        cls, v: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate required properties for agent_message_received event."""
        required_fields = ["message_id", "response_text"]
        missing = [f for f in required_fields if f not in v]
        if missing:
            raise ValueError(
                f"Missing required properties for agent_message_received: {', '.join(missing)}"
            )
        return v


# ============================================================================
# Session Events
# ============================================================================


class SessionStartedEvent(PlatformEvent):
    """
    Event emitted when a user session begins.

    Properties:
    - user_agent (str, optional): Browser user agent string
    - screen_width (int, optional): Browser screen width in pixels
    - screen_height (int, optional): Browser screen height in pixels
    - timezone (str, optional): User's timezone (e.g., 'America/Los_Angeles')
    - language (str, optional): Browser language (e.g., 'en-US')

    Example:
        {
            "event_name": "session_started",
            "session_id": "abc-123",
            "user_id": "user-456",
            "properties": {
                "user_agent": "Mozilla/5.0...",
                "screen_width": 1920,
                "screen_height": 1080,
                "timezone": "America/Los_Angeles",
                "language": "en-US"
            }
        }
    """

    event_name: Literal["session_started"] = "session_started"


# ============================================================================
# Event Type Union (for validation)
# ============================================================================

# Union type for all event types
PlatformEventType = (
    TaskCreatedEvent
    | TaskCompletedEvent
    | TaskDeletedEvent
    | TaskUpdatedEvent
    | PageViewedEvent
    | AgentMessageSentEvent
    | AgentMessageReceivedEvent
    | SessionStartedEvent
)
