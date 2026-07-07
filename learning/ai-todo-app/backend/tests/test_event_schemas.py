"""Tests for Platform Event Schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.event_schemas.events import (
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


class TestPlatformEvent:
    """Test suite for base PlatformEvent schema."""

    def test_platform_event_with_all_fields(self):
        """Test creating event with all required fields."""
        event = PlatformEvent(
            event_id="test-id",
            event_name="test_event",
            event_version="v1",
            timestamp="2024-01-15T10:30:00Z",
            session_id="session-123",
            user_id="user-456",
            properties={"key": "value"}
        )

        assert event.event_id == "test-id"
        assert event.event_name == "test_event"
        assert event.event_version == "v1"
        assert event.session_id == "session-123"
        assert event.user_id == "user-456"
        assert event.properties == {"key": "value"}

    def test_platform_event_auto_generates_metadata(self):
        """Test that missing metadata fields are auto-generated."""
        event = PlatformEvent(
            event_name="test_event",
            session_id="session-123",
            user_id="user-456"
        )

        # Auto-generated fields should exist
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.event_version == "v1"

    def test_platform_event_validates_timestamp_format(self):
        """Test that invalid timestamp format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PlatformEvent(
                event_name="test_event",
                timestamp="invalid-timestamp",
                session_id="session-123",
                user_id="user-456"
            )

        assert "Invalid timestamp format" in str(exc_info.value)

    def test_platform_event_validates_event_version_pattern(self):
        """Test that event_version must match pattern v{number}."""
        with pytest.raises(ValidationError) as exc_info:
            PlatformEvent(
                event_name="test_event",
                event_version="invalid",
                session_id="session-123",
                user_id="user-456"
            )

        assert "pattern" in str(exc_info.value).lower()

    def test_platform_event_requires_session_id(self):
        """Test that session_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlatformEvent(
                event_name="test_event",
                user_id="user-456"
            )

        assert "session_id" in str(exc_info.value)

    def test_platform_event_requires_user_id(self):
        """Test that user_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlatformEvent(
                event_name="test_event",
                session_id="session-123"
            )

        assert "user_id" in str(exc_info.value)


class TestTaskCreatedEvent:
    """Test suite for TaskCreatedEvent schema."""

    def test_task_created_event_valid(self):
        """Test creating valid task_created event."""
        event = TaskCreatedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "task_id": "task-789",
                "title": "Buy milk",
                "description": "Get 2% milk",
                "status": "pending",
                "priority": "high"
            }
        )

        assert event.event_name == "task_created"
        assert event.properties["task_id"] == "task-789"
        assert event.properties["title"] == "Buy milk"

    def test_task_created_event_requires_task_id(self):
        """Test that task_id is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreatedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "title": "Buy milk",
                    "status": "pending"
                }
            )

        assert "task_id" in str(exc_info.value)

    def test_task_created_event_requires_title(self):
        """Test that title is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreatedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "task_id": "task-789",
                    "status": "pending"
                }
            )

        assert "title" in str(exc_info.value)

    def test_task_created_event_requires_status(self):
        """Test that status is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreatedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "task_id": "task-789",
                    "title": "Buy milk"
                }
            )

        assert "status" in str(exc_info.value)


class TestTaskCompletedEvent:
    """Test suite for TaskCompletedEvent schema."""

    def test_task_completed_event_valid(self):
        """Test creating valid task_completed event."""
        event = TaskCompletedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "task_id": "task-789",
                "title": "Buy milk",
                "completed_at": "2024-01-15T11:00:00Z",
                "time_to_complete_seconds": 1800
            }
        )

        assert event.event_name == "task_completed"
        assert event.properties["task_id"] == "task-789"
        assert event.properties["completed_at"] == "2024-01-15T11:00:00Z"

    def test_task_completed_event_requires_completed_at(self):
        """Test that completed_at is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCompletedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "task_id": "task-789",
                    "title": "Buy milk"
                }
            )

        assert "completed_at" in str(exc_info.value)


class TestTaskDeletedEvent:
    """Test suite for TaskDeletedEvent schema."""

    def test_task_deleted_event_valid(self):
        """Test creating valid task_deleted event."""
        event = TaskDeletedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "task_id": "task-789",
                "title": "Buy milk",
                "status": "pending"
            }
        )

        assert event.event_name == "task_deleted"
        assert event.properties["task_id"] == "task-789"


class TestTaskUpdatedEvent:
    """Test suite for TaskUpdatedEvent schema."""

    def test_task_updated_event_valid(self):
        """Test creating valid task_updated event."""
        event = TaskUpdatedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "task_id": "task-789",
                "title": "Buy milk",
                "updated_fields": ["priority", "due_date"],
                "previous_values": {"priority": "low", "due_date": None},
                "current_values": {"priority": "high", "due_date": "2024-01-16T18:00:00Z"}
            }
        )

        assert event.event_name == "task_updated"
        assert event.properties["updated_fields"] == ["priority", "due_date"]

    def test_task_updated_event_requires_updated_fields(self):
        """Test that updated_fields is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdatedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "task_id": "task-789",
                    "title": "Buy milk",
                    "current_values": {"priority": "high"}
                }
            )

        assert "updated_fields" in str(exc_info.value)

    def test_task_updated_event_requires_current_values(self):
        """Test that current_values is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdatedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "task_id": "task-789",
                    "title": "Buy milk",
                    "updated_fields": ["priority"]
                }
            )

        assert "current_values" in str(exc_info.value)


class TestPageViewedEvent:
    """Test suite for PageViewedEvent schema."""

    def test_page_viewed_event_valid(self):
        """Test creating valid page_viewed event."""
        event = PageViewedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "page_path": "/tasks",
                "page_title": "My Tasks",
                "referrer": "/dashboard"
            }
        )

        assert event.event_name == "page_viewed"
        assert event.properties["page_path"] == "/tasks"

    def test_page_viewed_event_requires_page_path(self):
        """Test that page_path is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            PageViewedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "page_title": "My Tasks"
                }
            )

        assert "page_path" in str(exc_info.value)


class TestAgentMessageSentEvent:
    """Test suite for AgentMessageSentEvent schema."""

    def test_agent_message_sent_event_valid(self):
        """Test creating valid agent_message_sent event."""
        event = AgentMessageSentEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "message_id": "msg-001",
                "message_text": "Create a task to buy milk",
                "message_length": 26,
                "conversation_id": "conv-789"
            }
        )

        assert event.event_name == "agent_message_sent"
        assert event.properties["message_id"] == "msg-001"

    def test_agent_message_sent_event_requires_message_id(self):
        """Test that message_id is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            AgentMessageSentEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "message_text": "Create a task"
                }
            )

        assert "message_id" in str(exc_info.value)

    def test_agent_message_sent_event_requires_message_text(self):
        """Test that message_text is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            AgentMessageSentEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "message_id": "msg-001"
                }
            )

        assert "message_text" in str(exc_info.value)


class TestAgentMessageReceivedEvent:
    """Test suite for AgentMessageReceivedEvent schema."""

    def test_agent_message_received_event_valid(self):
        """Test creating valid agent_message_received event."""
        event = AgentMessageReceivedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "message_id": "msg-002",
                "response_text": "I created the task",
                "response_length": 19,
                "conversation_id": "conv-789",
                "user_message_id": "msg-001",
                "response_time_ms": 1250
            }
        )

        assert event.event_name == "agent_message_received"
        assert event.properties["message_id"] == "msg-002"

    def test_agent_message_received_event_requires_response_text(self):
        """Test that response_text is required in properties."""
        with pytest.raises(ValidationError) as exc_info:
            AgentMessageReceivedEvent(
                session_id="session-123",
                user_id="user-456",
                properties={
                    "message_id": "msg-002"
                }
            )

        assert "response_text" in str(exc_info.value)


class TestSessionStartedEvent:
    """Test suite for SessionStartedEvent schema."""

    def test_session_started_event_valid(self):
        """Test creating valid session_started event."""
        event = SessionStartedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "user_agent": "Mozilla/5.0...",
                "screen_width": 1920,
                "screen_height": 1080,
                "timezone": "America/Los_Angeles",
                "language": "en-US"
            }
        )

        assert event.event_name == "session_started"
        assert event.properties["screen_width"] == 1920

    def test_session_started_event_allows_empty_properties(self):
        """Test that session_started allows empty properties."""
        event = SessionStartedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={}
        )

        assert event.event_name == "session_started"
        assert event.properties == {}


class TestEventSerialization:
    """Test suite for event serialization."""

    def test_event_to_dict(self):
        """Test that events can be serialized to dict."""
        event = TaskCreatedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "task_id": "task-789",
                "title": "Buy milk",
                "status": "pending"
            }
        )

        event_dict = event.model_dump()

        assert isinstance(event_dict, dict)
        assert event_dict["event_name"] == "task_created"
        assert event_dict["session_id"] == "session-123"
        assert event_dict["properties"]["task_id"] == "task-789"

    def test_event_to_json(self):
        """Test that events can be serialized to JSON."""
        event = TaskCreatedEvent(
            session_id="session-123",
            user_id="user-456",
            properties={
                "task_id": "task-789",
                "title": "Buy milk",
                "status": "pending"
            }
        )

        event_json = event.model_dump_json()

        assert isinstance(event_json, str)
        assert "task_created" in event_json
        assert "session-123" in event_json

    def test_event_from_dict(self):
        """Test that events can be deserialized from dict."""
        event_dict = {
            "event_id": "test-id",
            "event_name": "task_created",
            "event_version": "v1",
            "timestamp": "2024-01-15T10:30:00Z",
            "session_id": "session-123",
            "user_id": "user-456",
            "properties": {
                "task_id": "task-789",
                "title": "Buy milk",
                "status": "pending"
            }
        }

        event = TaskCreatedEvent(**event_dict)

        assert event.event_name == "task_created"
        assert event.session_id == "session-123"
        assert event.properties["task_id"] == "task-789"
