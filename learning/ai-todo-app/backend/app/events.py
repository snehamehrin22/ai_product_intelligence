"""Zerobus Event Publisher Service.

Publishes platform events and agent traces to Databricks Delta Lake via Zerobus Ingest.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Literal
from contextlib import contextmanager

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .config import settings

# Zerobus SDK imports (only if configured)
try:
    from zerobus.sdk.sync import ZerobusSdk
    from zerobus.sdk.shared import RecordType, StreamConfigurationOptions, TableProperties
    ZEROBUS_AVAILABLE = True
except ImportError:
    ZEROBUS_AVAILABLE = False
    logging.warning("Zerobus SDK not installed. Event publishing will be disabled.")


logger = logging.getLogger(__name__)


TableType = Literal["platform_events", "agent_traces"]


class ZerobusPublisher:
    """
    Publisher for sending events to Databricks Delta Lake via Zerobus Ingest.

    Features:
    - Async wrapper for FastAPI compatibility
    - Retry logic with exponential backoff
    - Connection pooling via stream reuse
    - Automatic metadata addition (event_id, timestamp)
    - Graceful error handling

    Usage:
        publisher = ZerobusPublisher()
        await publisher.publish(event_data, table="platform_events")
        await publisher.close()
    """

    def __init__(self):
        """Initialize Zerobus publisher with SDK connection."""
        self._sdk: Optional[ZerobusSdk] = None
        self._streams: Dict[str, Any] = {}  # table_name -> stream
        self._lock = asyncio.Lock()
        self._initialized = False

        # Configuration
        self.zerobus_endpoint = settings.databricks_zerobus_endpoint
        self.workspace_url = settings.databricks_workspace_url
        self.client_id = settings.databricks_client_id
        self.client_secret = settings.databricks_client_secret

        # Validate configuration
        if not all([self.zerobus_endpoint, self.workspace_url, self.client_id, self.client_secret]):
            logger.warning(
                "Zerobus configuration incomplete. Event publishing will be disabled. "
                "Set DATABRICKS_ZEROBUS_ENDPOINT, DATABRICKS_WORKSPACE_URL, "
                "DATABRICKS_CLIENT_ID, and DATABRICKS_CLIENT_SECRET."
            )
            self._enabled = False
        elif not ZEROBUS_AVAILABLE:
            logger.warning("Zerobus SDK not available. Install with: pip install databricks-zerobus-ingest-sdk")
            self._enabled = False
        else:
            self._enabled = True
            logger.info(f"Zerobus publisher initialized for endpoint: {self.zerobus_endpoint}")

    def _initialize_sdk(self):
        """Initialize Zerobus SDK (lazy initialization)."""
        if self._initialized or not self._enabled:
            return

        try:
            self._sdk = ZerobusSdk(
                self.zerobus_endpoint,
                unity_catalog_url=self.workspace_url
            )
            self._initialized = True
            logger.info("Zerobus SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Zerobus SDK: {e}")
            self._enabled = False
            raise

    def _get_table_name(self, table: TableType) -> str:
        """Get fully qualified table name."""
        catalog = settings.databricks_catalog or "signaltogrowth"
        schema = "bronze"
        return f"{catalog}.{schema}.{table}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _create_stream(self, table: TableType):
        """
        Create Zerobus stream for a table (with retry logic).

        Args:
            table: Table type (platform_events or agent_traces)

        Returns:
            Zerobus stream object

        Raises:
            Exception: If stream creation fails after retries
        """
        if not self._enabled:
            raise RuntimeError("Zerobus publisher is not enabled")

        self._initialize_sdk()

        table_name = self._get_table_name(table)
        table_properties = TableProperties(table_name)
        options = StreamConfigurationOptions(record_type=RecordType.JSON)

        logger.info(f"Creating Zerobus stream for table: {table_name}")

        stream = self._sdk.create_stream(
            self.client_id,
            self.client_secret,
            table_properties,
            options
        )

        logger.info(f"Zerobus stream created for {table_name}")
        return stream

    def _get_or_create_stream(self, table: TableType):
        """
        Get existing stream or create new one (connection pooling).

        Args:
            table: Table type

        Returns:
            Zerobus stream object
        """
        if table not in self._streams:
            self._streams[table] = self._create_stream(table)
        return self._streams[table]

    def _add_metadata(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add automatic metadata to event if missing.

        Args:
            event: Event dictionary

        Returns:
            Event with metadata added
        """
        enriched = event.copy()

        # Add event_id if missing
        if "event_id" not in enriched:
            enriched["event_id"] = str(uuid.uuid4())

        # Add timestamp if missing (ISO8601 with timezone)
        if "timestamp" not in enriched:
            enriched["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Add event_version if missing
        if "event_version" not in enriched:
            enriched["event_version"] = "v1"

        return enriched

    def _publish_sync(self, event: Dict[str, Any], table: TableType):
        """
        Synchronous publish method (internal).

        Args:
            event: Event data dictionary
            table: Target table

        Raises:
            Exception: If publishing fails after retries
        """
        if not self._enabled:
            logger.debug(f"Zerobus disabled, skipping event: {event.get('event_name', 'unknown')}")
            return

        try:
            # Add metadata
            enriched_event = self._add_metadata(event)

            # Get or create stream
            stream = self._get_or_create_stream(table)

            # Publish event
            offset = stream.ingest_record_offset(enriched_event)

            logger.debug(
                f"Published event {enriched_event['event_id']} to {table} "
                f"(offset: {offset}, event: {enriched_event.get('event_name', 'unknown')})"
            )

        except Exception as e:
            logger.error(f"Failed to publish event to {table}: {e}", exc_info=True)
            # Don't re-raise - graceful degradation (log error but don't crash app)

    async def publish(
        self,
        event: Dict[str, Any],
        table: TableType = "platform_events"
    ):
        """
        Publish event to Zerobus (async wrapper for FastAPI).

        Args:
            event: Event data dictionary with fields:
                - event_name (str): Event type
                - session_id (str): User session ID
                - user_id (str): User identifier
                - properties (dict): Event-specific data
                - event_id (str, optional): Auto-generated if missing
                - timestamp (str, optional): Auto-generated if missing
                - event_version (str, optional): Defaults to "v1"
            table: Target table ("platform_events" or "agent_traces")

        Example:
            await publisher.publish({
                "event_name": "task_created",
                "session_id": "abc-123",
                "user_id": "user-1",
                "properties": {"task_id": "task-456", "title": "Buy milk"}
            })
        """
        async with self._lock:
            await asyncio.to_thread(self._publish_sync, event, table)

    async def flush(self, table: Optional[TableType] = None):
        """
        Flush Zerobus stream buffers to ensure writes complete.

        Args:
            table: Specific table to flush, or None to flush all streams
        """
        if not self._enabled:
            return

        async def _flush_stream(stream):
            try:
                await asyncio.to_thread(stream.flush)
                logger.debug("Zerobus stream flushed")
            except Exception as e:
                logger.error(f"Failed to flush stream: {e}")

        if table:
            if table in self._streams:
                await _flush_stream(self._streams[table])
        else:
            # Flush all streams
            for stream in self._streams.values():
                await _flush_stream(stream)

    async def close(self):
        """
        Close all Zerobus streams gracefully.

        Should be called on application shutdown.
        """
        if not self._enabled:
            return

        logger.info("Closing Zerobus publisher...")

        for table_name, stream in self._streams.items():
            try:
                await asyncio.to_thread(stream.close)
                logger.info(f"Closed Zerobus stream for {table_name}")
            except Exception as e:
                logger.error(f"Error closing stream for {table_name}: {e}")

        self._streams.clear()
        self._initialized = False
        logger.info("Zerobus publisher closed")

    def __del__(self):
        """Cleanup on deletion (best effort)."""
        if self._streams:
            logger.warning("ZerobusPublisher deleted without calling close(). Streams may not be flushed.")


# Global publisher instance (singleton)
_publisher: Optional[ZerobusPublisher] = None


def get_zerobus_publisher() -> ZerobusPublisher:
    """
    Get global Zerobus publisher instance (dependency injection for FastAPI).

    Returns:
        ZerobusPublisher instance

    Example:
        @app.post("/tasks")
        async def create_task(
            task: TaskCreate,
            publisher: ZerobusPublisher = Depends(get_zerobus_publisher)
        ):
            # ... create task ...
            await publisher.publish({
                "event_name": "task_created",
                "session_id": session_id,
                "user_id": task.user_id,
                "properties": {"task_id": new_task.id}
            })
    """
    global _publisher
    if _publisher is None:
        _publisher = ZerobusPublisher()
    return _publisher
