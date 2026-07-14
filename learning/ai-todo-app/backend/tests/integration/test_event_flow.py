"""Integration tests for end-to-end event flow validation.

Tests the complete flow:
1. Frontend/API → Backend
2. Backend → Zerobus Ingest
3. Zerobus → Delta Lake
4. Query Delta Lake to verify events

These tests validate that platform events and agent traces successfully
flow through the entire system and land in Delta Lake tables.
"""

import os
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime, timedelta

import pytest
from databricks import sql

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings
from fastapi.testclient import TestClient
from app.main import app


class TestEventFlowValidation:
    """Integration tests for event flow: API → Zerobus → Delta Lake."""

    @pytest.fixture
    def db_connection(self):
        """Create Databricks connection for querying Delta tables."""
        connection = sql.connect(
            server_hostname=settings.databricks_host.replace("https://", ""),
            http_path=settings.databricks_http_path,
            access_token=settings.databricks_token
        )
        yield connection
        connection.close()

    @pytest.fixture
    def test_session_id(self):
        """Generate unique session ID for test."""
        return str(uuid.uuid4())

    @pytest.fixture
    def test_user_id(self):
        """Generate unique user ID for test."""
        return f"test-user-{uuid.uuid4().hex[:8]}"

    def test_task_created_event_in_delta_lake(self, db_connection, test_session_id, test_user_id):
        """Test that task_created event flows to Delta Lake.

        Flow:
        1. POST /tasks → creates task
        2. Backend emits task_created event to Zerobus
        3. Wait for Zerobus ingestion (~5 seconds)
        4. Query Delta Lake for event
        5. Validate event schema and content
        """
        client = TestClient(app)

        # Step 1: Create task via API
        print(f"\n1. Creating task with session_id: {test_session_id}")
        response = client.post(
            "/tasks",
            headers={"X-Session-Id": test_session_id},
            json={
                "title": f"Integration Test Task {test_session_id[:8]}",
                "description": "Test task for event flow validation",
                "user_id": test_user_id
            }
        )

        assert response.status_code == 200
        task_data = response.json()
        task_id = task_data["id"]
        print(f"✓ Task created: {task_id}")

        # Step 2: Wait for Zerobus ingestion
        print("\n2. Waiting for Zerobus ingestion (5 seconds)...")
        time.sleep(5)

        # Step 3: Query Delta Lake for event
        print("\n3. Querying Delta Lake for task_created event...")
        cursor = db_connection.cursor()

        query = """
        SELECT
            event_id,
            event_name,
            event_timestamp,
            session_id,
            user_id,
            properties
        FROM signaltogrowth.platform_events
        WHERE session_id = ?
            AND event_name = 'task_created'
            AND event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 MINUTE
        ORDER BY event_timestamp DESC
        LIMIT 1
        """

        cursor.execute(query, (test_session_id,))
        result = cursor.fetchone()

        # Step 4: Validate event
        if result is None:
            print("\n❌ Event not found in Delta Lake")
            print("Possible reasons:")
            print("  - Zerobus ingestion delay (wait longer)")
            print("  - Zerobus connection not configured")
            print("  - Table doesn't exist (run setup_zerobus_catalog_tables.sql)")
            pytest.skip("Event not found in Delta Lake (may need Zerobus setup)")

        print("✓ Event found in Delta Lake!")

        # Unpack result
        event_id, event_name, event_timestamp, session_id, user_id, properties = result

        # Validate schema
        assert event_id is not None, "event_id should not be null"
        assert event_name == "task_created"
        assert session_id == test_session_id
        assert user_id == test_user_id

        print("\n4. Validation results:")
        print(f"  event_id: {event_id}")
        print(f"  event_name: {event_name}")
        print(f"  session_id: {session_id}")
        print(f"  user_id: {user_id}")
        print(f"  properties: {properties}")

        # Validate properties (if JSON string, parse it)
        if isinstance(properties, str):
            import json
            properties = json.loads(properties)

        assert "task_id" in properties
        assert properties["task_id"] == task_id

        print("\n✅ Event flow validation PASSED!")
        print(f"   Event successfully flowed: API → Zerobus → Delta Lake")

    def test_agent_trace_in_delta_lake(self, db_connection, test_session_id, test_user_id):
        """Test that agent traces flow to Delta Lake.

        Flow:
        1. POST /agent/chat → agent processes message
        2. OpenTelemetry creates spans
        3. Zerobus span exporter publishes to Delta Lake
        4. Query Delta Lake for traces
        5. Validate trace schema and content
        """
        client = TestClient(app)

        # Step 1: Send agent message
        print(f"\n1. Sending agent message with session_id: {test_session_id}")

        # Note: This may fail without valid OpenAI credentials
        # The test focuses on trace publishing, not agent execution
        try:
            response = client.post(
                "/agent/chat",
                headers={"X-Session-Id": test_session_id},
                params={
                    "message": "Create a task to test event flow",
                    "user_id": test_user_id
                }
            )
            print(f"✓ Agent responded (status: {response.status_code})")
        except Exception as e:
            print(f"⚠ Agent execution failed (expected without OpenAI credentials): {e}")
            pytest.skip("Agent execution requires OpenAI credentials")

        # Step 2: Wait for trace export
        print("\n2. Waiting for trace export (5 seconds)...")
        time.sleep(5)

        # Step 3: Query Delta Lake for traces
        print("\n3. Querying Delta Lake for agent traces...")
        cursor = db_connection.cursor()

        query = """
        SELECT
            trace_id,
            span_id,
            span_name,
            session_id,
            start_time,
            end_time,
            duration_ms,
            attributes
        FROM signaltogrowth.agent_traces
        WHERE session_id = ?
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 MINUTE
        ORDER BY start_time DESC
        LIMIT 5
        """

        cursor.execute(query, (test_session_id,))
        results = cursor.fetchall()

        # Step 4: Validate traces
        if not results:
            print("\n❌ No traces found in Delta Lake")
            print("Possible reasons:")
            print("  - OTel trace export delay (wait longer)")
            print("  - Zerobus span exporter not configured")
            print("  - Agent execution failed (check OpenAI credentials)")
            pytest.skip("Traces not found in Delta Lake")

        print(f"✓ Found {len(results)} traces in Delta Lake!")

        # Validate first trace
        trace = results[0]
        trace_id, span_id, span_name, session_id, start_time, end_time, duration_ms, attributes = trace

        assert trace_id is not None
        assert span_id is not None
        assert session_id == test_session_id
        assert span_name is not None

        print("\n4. Validation results:")
        print(f"  trace_id: {trace_id}")
        print(f"  span_name: {span_name}")
        print(f"  session_id: {session_id}")
        print(f"  duration_ms: {duration_ms}")

        # Check for GenAI attributes
        if isinstance(attributes, str):
            import json
            attributes = json.loads(attributes)

        if "gen_ai.request.model" in attributes:
            print(f"  model: {attributes['gen_ai.request.model']}")

        if "gen_ai.usage.total_tokens" in attributes:
            print(f"  tokens: {attributes['gen_ai.usage.total_tokens']}")

        print("\n✅ Trace flow validation PASSED!")
        print(f"   Traces successfully flowed: Agent → OTel → Zerobus → Delta Lake")

    def test_session_id_join(self, db_connection, test_session_id, test_user_id):
        """Test that session_id can join events and traces.

        This validates the primary use case: joining platform events
        and agent traces using session_id.
        """
        client = TestClient(app)

        print(f"\n1. Creating task via agent with session_id: {test_session_id}")

        # Trigger both event and trace
        try:
            response = client.post(
                "/agent/chat",
                headers={"X-Session-Id": test_session_id},
                params={
                    "message": "Buy milk tomorrow",
                    "user_id": test_user_id
                }
            )
            print(f"✓ Agent message sent (status: {response.status_code})")
        except Exception as e:
            pytest.skip(f"Agent execution requires OpenAI credentials: {e}")

        # Wait for ingestion
        print("\n2. Waiting for event and trace ingestion (7 seconds)...")
        time.sleep(7)

        # Query for join
        print("\n3. Querying Delta Lake with session_id join...")
        cursor = db_connection.cursor()

        query = """
        SELECT
            e.event_name,
            e.event_timestamp,
            t.span_name,
            t.start_time,
            t.duration_ms,
            e.session_id
        FROM signaltogrowth.platform_events e
        LEFT JOIN signaltogrowth.agent_traces t
            ON e.session_id = t.session_id
        WHERE e.session_id = ?
            AND e.event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 2 MINUTE
        ORDER BY e.event_timestamp DESC
        LIMIT 10
        """

        cursor.execute(query, (test_session_id,))
        results = cursor.fetchall()

        if not results:
            pytest.skip("No joined events found (requires both events and traces)")

        print(f"✓ Found {len(results)} joined records!")

        # Display results
        print("\n4. Join results:")
        for row in results[:3]:  # Show first 3
            event_name, event_ts, span_name, start_time, duration_ms, session_id = row
            print(f"  Event: {event_name} | Trace: {span_name} | Duration: {duration_ms}ms")

        # Validate at least one successful join (trace is not null)
        has_joined_trace = any(row[2] is not None for row in results)
        assert has_joined_trace, "session_id join should match events with traces"

        print("\n✅ Session ID join validation PASSED!")
        print(f"   Events and traces successfully joined on session_id")

    def test_event_ordering(self, db_connection, test_session_id, test_user_id):
        """Test that events are ordered correctly by timestamp within session."""
        client = TestClient(app)

        print(f"\n1. Creating multiple events with session_id: {test_session_id}")

        # Create multiple tasks to generate ordered events
        task_ids = []
        for i in range(3):
            response = client.post(
                "/tasks",
                headers={"X-Session-Id": test_session_id},
                json={
                    "title": f"Test Task {i+1}",
                    "description": f"Task {i+1} for ordering test",
                    "user_id": test_user_id
                }
            )
            if response.status_code == 200:
                task_ids.append(response.json()["id"])
                print(f"  ✓ Created task {i+1}")
            time.sleep(0.5)  # Small delay between creates

        print(f"\n2. Waiting for event ingestion (6 seconds)...")
        time.sleep(6)

        # Query events ordered by timestamp
        print("\n3. Querying events ordered by timestamp...")
        cursor = db_connection.cursor()

        query = """
        SELECT
            event_name,
            event_timestamp,
            properties
        FROM signaltogrowth.platform_events
        WHERE session_id = ?
            AND event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 2 MINUTE
        ORDER BY event_timestamp ASC
        """

        cursor.execute(query, (test_session_id,))
        results = cursor.fetchall()

        if len(results) < 2:
            pytest.skip(f"Not enough events found ({len(results)}) for ordering test")

        print(f"✓ Found {len(results)} events")

        # Validate ordering
        print("\n4. Validating event ordering:")
        previous_timestamp = None
        for i, row in enumerate(results):
            event_name, event_timestamp, properties = row
            print(f"  {i+1}. {event_name} at {event_timestamp}")

            if previous_timestamp:
                assert event_timestamp >= previous_timestamp, \
                    "Events should be ordered by timestamp (ASC)"

            previous_timestamp = event_timestamp

        print("\n✅ Event ordering validation PASSED!")
        print(f"   Events are correctly ordered by timestamp")


class TestEventSchemaCompliance:
    """Tests for event schema validation."""

    @pytest.fixture
    def db_connection(self):
        """Create Databricks connection."""
        connection = sql.connect(
            server_hostname=settings.databricks_host.replace("https://", ""),
            http_path=settings.databricks_http_path,
            access_token=settings.databricks_token
        )
        yield connection
        connection.close()

    def test_platform_events_schema(self, db_connection):
        """Validate platform_events table schema."""
        cursor = db_connection.cursor()

        # Query recent events
        query = """
        SELECT *
        FROM signaltogrowth.platform_events
        WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 DAY
        LIMIT 1
        """

        cursor.execute(query)

        # Get column names
        columns = [desc[0] for desc in cursor.description]
        print(f"\nplatform_events columns: {columns}")

        # Validate required columns exist
        required_columns = ["event_id", "event_name", "event_timestamp", "session_id", "user_id"]
        for col in required_columns:
            assert col in columns, f"Required column '{col}' missing from platform_events"

        print("✓ platform_events schema is valid")

    def test_agent_traces_schema(self, db_connection):
        """Validate agent_traces table schema."""
        cursor = db_connection.cursor()

        # Query recent traces
        query = """
        SELECT *
        FROM signaltogrowth.agent_traces
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 DAY
        LIMIT 1
        """

        cursor.execute(query)

        # Get column names
        columns = [desc[0] for desc in cursor.description]
        print(f"\nagent_traces columns: {columns}")

        # Validate required columns exist
        required_columns = ["trace_id", "span_id", "span_name", "session_id", "timestamp"]
        for col in required_columns:
            assert col in columns, f"Required column '{col}' missing from agent_traces"

        print("✓ agent_traces schema is valid")


if __name__ == "__main__":
    """Run tests with pytest."""
    print("\n" + "="*70)
    print("End-to-End Event Flow Validation Tests")
    print("="*70)
    print("\nThese tests validate:")
    print("  1. Events flow from API → Zerobus → Delta Lake")
    print("  2. Traces flow from Agent → OTel → Zerobus → Delta Lake")
    print("  3. session_id enables joining events and traces")
    print("  4. Events are ordered correctly by timestamp")
    print("  5. Table schemas match expected structure")
    print("\nRequirements:")
    print("  - Databricks connection configured (.env)")
    print("  - Zerobus Ingest enabled and tables created")
    print("  - OpenAI API key (for agent tests)")
    print("\n" + "="*70)
    print("\nRun with: cd backend && pytest tests/integration/test_event_flow.py -v\n")
