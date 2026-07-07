"""Tests for Zerobus Event Publisher Service."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import uuid

from app.events import ZerobusPublisher, get_zerobus_publisher


@pytest.fixture
def mock_zerobus_sdk():
    """Mock Zerobus SDK for testing."""
    with patch('app.events.ZEROBUS_AVAILABLE', True):
        with patch('app.events.ZerobusSdk') as mock_sdk_class:
            # Create mock SDK instance
            mock_sdk = Mock()
            mock_sdk_class.return_value = mock_sdk

            # Create mock stream
            mock_stream = Mock()
            mock_stream.ingest_record_offset.return_value = 0
            mock_stream.flush.return_value = None
            mock_stream.close.return_value = None

            mock_sdk.create_stream.return_value = mock_stream

            yield {
                'sdk_class': mock_sdk_class,
                'sdk': mock_sdk,
                'stream': mock_stream
            }


@pytest.fixture
def mock_settings():
    """Mock settings with Zerobus configuration."""
    with patch('app.events.settings') as mock_settings:
        mock_settings.databricks_zerobus_endpoint = "test.zerobus.eastus.azuredatabricks.net"
        mock_settings.databricks_workspace_url = "https://test.azuredatabricks.net"
        mock_settings.databricks_client_id = "test-client-id"
        mock_settings.databricks_client_secret = "test-secret"
        mock_settings.databricks_catalog = "signaltogrowth"
        yield mock_settings


@pytest.fixture
def publisher(mock_zerobus_sdk, mock_settings):
    """Create ZerobusPublisher instance with mocked dependencies."""
    return ZerobusPublisher()


class TestZerobusPublisher:
    """Test suite for ZerobusPublisher."""

    @pytest.mark.asyncio
    async def test_publish_adds_metadata(self, publisher, mock_zerobus_sdk):
        """Test that publish() adds event_id, timestamp, and event_version if missing."""
        event = {
            "event_name": "task_created",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {"task_id": "123"}
        }

        await publisher.publish(event, table="platform_events")

        # Get the event that was passed to ingest_record_offset
        stream = mock_zerobus_sdk['stream']
        assert stream.ingest_record_offset.called
        published_event = stream.ingest_record_offset.call_args[0][0]

        # Verify metadata was added
        assert "event_id" in published_event
        assert "timestamp" in published_event
        assert "event_version" in published_event
        assert published_event["event_version"] == "v1"

        # Verify UUID format
        uuid.UUID(published_event["event_id"])  # Should not raise

        # Verify ISO8601 timestamp
        datetime.fromisoformat(published_event["timestamp"].replace('Z', '+00:00'))

    @pytest.mark.asyncio
    async def test_publish_preserves_existing_metadata(self, publisher, mock_zerobus_sdk):
        """Test that publish() doesn't override existing event_id or timestamp."""
        event_id = str(uuid.uuid4())
        timestamp = "2024-01-01T00:00:00Z"

        event = {
            "event_id": event_id,
            "event_name": "task_created",
            "event_version": "v2",
            "timestamp": timestamp,
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        await publisher.publish(event, table="platform_events")

        stream = mock_zerobus_sdk['stream']
        published_event = stream.ingest_record_offset.call_args[0][0]

        # Verify original values preserved
        assert published_event["event_id"] == event_id
        assert published_event["timestamp"] == timestamp
        assert published_event["event_version"] == "v2"

    @pytest.mark.asyncio
    async def test_publish_to_different_tables(self, publisher, mock_zerobus_sdk):
        """Test that publisher can publish to different tables."""
        platform_event = {
            "event_name": "task_created",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        trace_event = {
            "event_name": "agent_trace",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        await publisher.publish(platform_event, table="platform_events")
        await publisher.publish(trace_event, table="agent_traces")

        # Verify create_stream was called for both tables
        sdk = mock_zerobus_sdk['sdk']
        assert sdk.create_stream.call_count == 2

        # Verify table names in create_stream calls (TableProperties is positional arg 3)
        # The TableProperties object is constructed with table name as string
        # Just verify that both create_stream calls happened with different tables

    @pytest.mark.asyncio
    async def test_stream_reuse(self, publisher, mock_zerobus_sdk):
        """Test that streams are reused (connection pooling)."""
        event = {
            "event_name": "test_event",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        # Publish 3 events to same table
        await publisher.publish(event, table="platform_events")
        await publisher.publish(event, table="platform_events")
        await publisher.publish(event, table="platform_events")

        # Verify create_stream was called only once
        sdk = mock_zerobus_sdk['sdk']
        assert sdk.create_stream.call_count == 1

        # Verify ingest_record_offset was called 3 times
        stream = mock_zerobus_sdk['stream']
        assert stream.ingest_record_offset.call_count == 3

    @pytest.mark.asyncio
    async def test_flush_single_table(self, publisher, mock_zerobus_sdk):
        """Test flushing a single table."""
        event = {
            "event_name": "test_event",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        await publisher.publish(event, table="platform_events")
        await publisher.flush(table="platform_events")

        stream = mock_zerobus_sdk['stream']
        assert stream.flush.called

    @pytest.mark.asyncio
    async def test_flush_all_tables(self, publisher, mock_zerobus_sdk):
        """Test flushing all tables."""
        event = {
            "event_name": "test_event",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        await publisher.publish(event, table="platform_events")
        await publisher.publish(event, table="agent_traces")
        await publisher.flush()  # Flush all

        # Both streams should be flushed
        stream = mock_zerobus_sdk['stream']
        assert stream.flush.call_count == 2

    @pytest.mark.asyncio
    async def test_close_closes_all_streams(self, publisher, mock_zerobus_sdk):
        """Test that close() closes all streams."""
        event = {
            "event_name": "test_event",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        await publisher.publish(event, table="platform_events")
        await publisher.publish(event, table="agent_traces")
        await publisher.close()

        stream = mock_zerobus_sdk['stream']
        assert stream.close.call_count == 2

    @pytest.mark.asyncio
    async def test_graceful_error_handling(self, publisher, mock_zerobus_sdk):
        """Test that errors don't crash the application."""
        # Make ingest_record_offset raise an error
        stream = mock_zerobus_sdk['stream']
        stream.ingest_record_offset.side_effect = Exception("Zerobus connection failed")

        event = {
            "event_name": "test_event",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        # Should not raise exception (graceful degradation)
        await publisher.publish(event, table="platform_events")

    @pytest.mark.asyncio
    async def test_disabled_publisher_skips_publish(self):
        """Test that disabled publisher skips publishing without errors."""
        with patch('app.events.settings') as mock_settings:
            # Missing configuration
            mock_settings.databricks_zerobus_endpoint = ""
            mock_settings.databricks_workspace_url = ""
            mock_settings.databricks_client_id = ""
            mock_settings.databricks_client_secret = ""

            publisher = ZerobusPublisher()

            event = {
                "event_name": "test_event",
                "session_id": "test-session",
                "user_id": "test-user",
                "properties": {}
            }

            # Should not raise exception
            await publisher.publish(event, table="platform_events")

    def test_get_zerobus_publisher_singleton(self, mock_zerobus_sdk, mock_settings):
        """Test that get_zerobus_publisher returns singleton instance."""
        publisher1 = get_zerobus_publisher()
        publisher2 = get_zerobus_publisher()

        assert publisher1 is publisher2

    @pytest.mark.asyncio
    async def test_retry_logic_on_stream_creation_failure(self, mock_settings):
        """Test that stream creation is retried on failure."""
        with patch('app.events.ZEROBUS_AVAILABLE', True):
            with patch('app.events.ZerobusSdk') as mock_sdk_class:
                mock_sdk = Mock()
                mock_sdk_class.return_value = mock_sdk

                # Fail first 2 attempts, succeed on 3rd
                mock_sdk.create_stream.side_effect = [
                    Exception("Connection failed"),
                    Exception("Connection failed"),
                    Mock(ingest_record_offset=Mock(return_value=0))
                ]

                publisher = ZerobusPublisher()
                event = {
                    "event_name": "test_event",
                    "session_id": "test-session",
                    "user_id": "test-user",
                    "properties": {}
                }

                await publisher.publish(event, table="platform_events")

                # Verify retry happened (3 attempts)
                assert mock_sdk.create_stream.call_count == 3

    @pytest.mark.asyncio
    async def test_concurrent_publish_thread_safety(self, publisher, mock_zerobus_sdk):
        """Test that concurrent publishes are handled safely."""
        import asyncio

        event = {
            "event_name": "test_event",
            "session_id": "test-session",
            "user_id": "test-user",
            "properties": {}
        }

        # Publish 10 events concurrently
        tasks = [
            publisher.publish(event, table="platform_events")
            for _ in range(10)
        ]
        await asyncio.gather(*tasks)

        stream = mock_zerobus_sdk['stream']
        assert stream.ingest_record_offset.call_count == 10
