#!/usr/bin/env python3
"""Query script to read events and traces from Delta Lake.

This script provides a CLI interface to query platform events and agent traces
stored in Delta Lake via Zerobus Ingest.

Usage:
    # Query recent events
    python scripts/query_events.py events --limit 10

    # Query events for specific session
    python scripts/query_events.py events --session-id abc-123

    # Query agent traces
    python scripts/query_events.py traces --limit 10

    # Query joined events and traces
    python scripts/query_events.py join --session-id abc-123
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from app.config import settings


def get_connection():
    """Create Databricks connection."""
    return sql.connect(
        server_hostname=settings.databricks_host.replace("https://", ""),
        http_path=settings.databricks_http_path,
        access_token=settings.databricks_token
    )


def query_events(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    event_name: Optional[str] = None,
    hours: int = 24,
    limit: int = 10
):
    """Query platform events from Delta Lake.

    Args:
        session_id: Filter by session ID
        user_id: Filter by user ID
        event_name: Filter by event name
        hours: Look back N hours (default: 24)
        limit: Max results (default: 10)
    """
    print("\n" + "="*80)
    print("PLATFORM EVENTS QUERY")
    print("="*80)

    connection = get_connection()
    cursor = connection.cursor()

    # Build query
    query = """
    SELECT
        event_id,
        event_name,
        event_timestamp,
        session_id,
        user_id,
        properties
    FROM signaltogrowth.platform_events
    WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL ? HOUR
    """

    params = [hours]

    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    if event_name:
        query += " AND event_name = ?"
        params.append(event_name)

    query += " ORDER BY event_timestamp DESC LIMIT ?"
    params.append(limit)

    print(f"\nFilters:")
    print(f"  Time range: Last {hours} hours")
    if session_id:
        print(f"  Session ID: {session_id}")
    if user_id:
        print(f"  User ID: {user_id}")
    if event_name:
        print(f"  Event name: {event_name}")
    print(f"  Limit: {limit}")

    # Execute query
    print(f"\nExecuting query...")
    cursor.execute(query, params)
    results = cursor.fetchall()

    if not results:
        print("\n❌ No events found matching criteria")
        connection.close()
        return

    print(f"\n✓ Found {len(results)} events\n")

    # Display results
    for i, row in enumerate(results, 1):
        event_id, event_name, event_timestamp, session_id, user_id, properties = row

        print(f"Event {i}:")
        print(f"  ID: {event_id}")
        print(f"  Name: {event_name}")
        print(f"  Timestamp: {event_timestamp}")
        print(f"  Session: {session_id}")
        print(f"  User: {user_id}")

        # Parse properties if JSON string
        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except:
                pass

        if isinstance(properties, dict):
            print(f"  Properties:")
            for key, value in properties.items():
                print(f"    - {key}: {value}")
        else:
            print(f"  Properties: {properties}")

        print()

    connection.close()


def query_traces(
    session_id: Optional[str] = None,
    span_name: Optional[str] = None,
    hours: int = 24,
    limit: int = 10
):
    """Query agent traces from Delta Lake.

    Args:
        session_id: Filter by session ID
        span_name: Filter by span name
        hours: Look back N hours (default: 24)
        limit: Max results (default: 10)
    """
    print("\n" + "="*80)
    print("AGENT TRACES QUERY")
    print("="*80)

    connection = get_connection()
    cursor = connection.cursor()

    # Build query
    query = """
    SELECT
        trace_id,
        span_id,
        span_name,
        session_id,
        start_time,
        end_time,
        duration_ms,
        status_code,
        attributes
    FROM signaltogrowth.agent_traces
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL ? HOUR
    """

    params = [hours]

    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)

    if span_name:
        query += " AND span_name LIKE ?"
        params.append(f"%{span_name}%")

    query += " ORDER BY start_time DESC LIMIT ?"
    params.append(limit)

    print(f"\nFilters:")
    print(f"  Time range: Last {hours} hours")
    if session_id:
        print(f"  Session ID: {session_id}")
    if span_name:
        print(f"  Span name: {span_name}")
    print(f"  Limit: {limit}")

    # Execute query
    print(f"\nExecuting query...")
    cursor.execute(query, params)
    results = cursor.fetchall()

    if not results:
        print("\n❌ No traces found matching criteria")
        connection.close()
        return

    print(f"\n✓ Found {len(results)} traces\n")

    # Display results
    for i, row in enumerate(results, 1):
        trace_id, span_id, span_name, session_id, start_time, end_time, duration_ms, status_code, attributes = row

        print(f"Trace {i}:")
        print(f"  Trace ID: {trace_id}")
        print(f"  Span ID: {span_id}")
        print(f"  Span Name: {span_name}")
        print(f"  Session: {session_id}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        print(f"  Duration: {duration_ms}ms")
        print(f"  Status: {status_code}")

        # Parse attributes if JSON string
        if isinstance(attributes, str):
            try:
                attributes = json.loads(attributes)
            except:
                pass

        if isinstance(attributes, dict):
            print(f"  GenAI Attributes:")
            gen_ai_attrs = {k: v for k, v in attributes.items() if k.startswith("gen_ai.")}
            if gen_ai_attrs:
                for key, value in gen_ai_attrs.items():
                    print(f"    - {key}: {value}")
            else:
                print(f"    (no GenAI attributes)")

            # Show other interesting attributes
            other_attrs = ["user_id", "agent.task_created", "agent.needs_clarification"]
            for attr in other_attrs:
                if attr in attributes:
                    print(f"    - {attr}: {attributes[attr]}")

        print()

    connection.close()


def query_join(
    session_id: str,
    hours: int = 24,
    limit: int = 20
):
    """Query joined events and traces for a session.

    Args:
        session_id: Session ID to query (required)
        hours: Look back N hours (default: 24)
        limit: Max results (default: 20)
    """
    print("\n" + "="*80)
    print("SESSION TIMELINE (JOINED EVENTS + TRACES)")
    print("="*80)
    print(f"\nSession ID: {session_id}")
    print(f"Time range: Last {hours} hours")

    connection = get_connection()
    cursor = connection.cursor()

    # Query events and traces separately, then union for timeline
    query = """
    WITH events AS (
        SELECT
            event_timestamp as timestamp,
            'event' as type,
            event_name as name,
            event_id as id,
            properties as details
        FROM signaltogrowth.platform_events
        WHERE session_id = ?
            AND event_timestamp >= CURRENT_TIMESTAMP - INTERVAL ? HOUR
    ),
    traces AS (
        SELECT
            start_time as timestamp,
            'trace' as type,
            span_name as name,
            span_id as id,
            STRUCT(duration_ms, attributes) as details
        FROM signaltogrowth.agent_traces
        WHERE session_id = ?
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL ? HOUR
    )
    SELECT * FROM events
    UNION ALL
    SELECT * FROM traces
    ORDER BY timestamp ASC
    LIMIT ?
    """

    params = [session_id, hours, session_id, hours, limit]

    print(f"\nExecuting query...")
    cursor.execute(query, params)
    results = cursor.fetchall()

    if not results:
        print(f"\n❌ No events or traces found for session {session_id}")
        print("\nPossible reasons:")
        print("  - Session ID doesn't exist")
        print("  - Events outside time window")
        print("  - Zerobus ingestion delay")
        connection.close()
        return

    print(f"\n✓ Found {len(results)} events/traces\n")
    print("Timeline:")
    print("-" * 80)

    # Display timeline
    for row in results:
        timestamp, item_type, name, item_id, details = row

        icon = "📊" if item_type == "event" else "🔍"
        print(f"{icon} [{timestamp}] {item_type.upper()}: {name}")

        # Show relevant details
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                pass

        if isinstance(details, dict):
            # For events: show key properties
            if item_type == "event":
                key_props = ["task_id", "message_text", "task_created"]
                for prop in key_props:
                    if prop in details:
                        print(f"     └─ {prop}: {details[prop]}")

            # For traces: show duration and tokens
            elif item_type == "trace":
                if "duration_ms" in details:
                    print(f"     └─ duration: {details['duration_ms']}ms")
                if "attributes" in details:
                    attrs = details["attributes"]
                    if isinstance(attrs, dict) and "gen_ai.usage.total_tokens" in attrs:
                        print(f"     └─ tokens: {attrs['gen_ai.usage.total_tokens']}")

        print()

    connection.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Query events and traces from Delta Lake",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Recent events
  python scripts/query_events.py events --limit 10

  # Events for specific session
  python scripts/query_events.py events --session-id abc-123

  # Events for specific user
  python scripts/query_events.py events --user-id test-user-001

  # Filter by event name
  python scripts/query_events.py events --event-name task_created

  # Agent traces
  python scripts/query_events.py traces --limit 10

  # Traces for specific session
  python scripts/query_events.py traces --session-id abc-123

  # Session timeline (joined view)
  python scripts/query_events.py join --session-id abc-123
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Query command")

    # Events command
    events_parser = subparsers.add_parser("events", help="Query platform events")
    events_parser.add_argument("--session-id", help="Filter by session ID")
    events_parser.add_argument("--user-id", help="Filter by user ID")
    events_parser.add_argument("--event-name", help="Filter by event name")
    events_parser.add_argument("--hours", type=int, default=24, help="Look back N hours (default: 24)")
    events_parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")

    # Traces command
    traces_parser = subparsers.add_parser("traces", help="Query agent traces")
    traces_parser.add_argument("--session-id", help="Filter by session ID")
    traces_parser.add_argument("--span-name", help="Filter by span name (partial match)")
    traces_parser.add_argument("--hours", type=int, default=24, help="Look back N hours (default: 24)")
    traces_parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")

    # Join command
    join_parser = subparsers.add_parser("join", help="Query joined events and traces for session")
    join_parser.add_argument("--session-id", required=True, help="Session ID (required)")
    join_parser.add_argument("--hours", type=int, default=24, help="Look back N hours (default: 24)")
    join_parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "events":
            query_events(
                session_id=args.session_id,
                user_id=args.user_id,
                event_name=args.event_name,
                hours=args.hours,
                limit=args.limit
            )
        elif args.command == "traces":
            query_traces(
                session_id=args.session_id,
                span_name=args.span_name,
                hours=args.hours,
                limit=args.limit
            )
        elif args.command == "join":
            query_join(
                session_id=args.session_id,
                hours=args.hours,
                limit=args.limit
            )

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
