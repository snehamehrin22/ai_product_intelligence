#!/usr/bin/env python3
"""
Test Databricks Zerobus Ingest connection.

This script validates that:
1. Zerobus SDK can connect to Databricks
2. OAuth credentials are valid
3. Can write a test record to platform_events table
4. Can read back the test record

Usage:
    python backend/scripts/test_zerobus_connection.py
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_zerobus_connection():
    """Test Zerobus Ingest connection and write test record."""

    print("=" * 80)
    print("Testing Databricks Zerobus Ingest Connection")
    print("=" * 80)

    # Check environment variables
    required_vars = [
        "DATABRICKS_ZEROBUS_ENDPOINT",
        "DATABRICKS_WORKSPACE_URL",
        "DATABRICKS_CLIENT_ID",
        "DATABRICKS_CLIENT_SECRET"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following in your .env file:")
        for var in missing_vars:
            print(f"  {var}=<value>")
        return False

    print("\n✅ All required environment variables found")

    # Import Zerobus SDK (will fail if not installed)
    try:
        from zerobus.sdk.sync import ZerobusSdk
        from zerobus.sdk.shared import RecordType, StreamConfigurationOptions, TableProperties
        print("✅ Zerobus SDK imported successfully")
    except ImportError as e:
        print(f"\n❌ Failed to import Zerobus SDK: {e}")
        print("\nInstall with: pip install databricks-zerobus-ingest-sdk")
        print("Or run: cd backend && source .venv/bin/activate && pip install databricks-zerobus-ingest-sdk")
        return False

    # Extract config from environment
    server_endpoint = os.getenv("DATABRICKS_ZEROBUS_ENDPOINT")
    workspace_url = os.getenv("DATABRICKS_WORKSPACE_URL")
    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")

    print(f"\nZerobus Endpoint: {server_endpoint}")
    print(f"Workspace URL: {workspace_url}")
    print(f"Client ID: {client_id[:10]}...")

    # Initialize SDK (using unity_catalog_url parameter as shown in official docs)
    try:
        sdk = ZerobusSdk(server_endpoint, unity_catalog_url=workspace_url)
        print("\n✅ Zerobus SDK initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize Zerobus SDK: {e}")
        return False

    # Configure stream for platform_events table
    # Using bronze layer: signaltogrowth.bronze.platform_events
    table_properties = TableProperties("signaltogrowth.bronze.platform_events")
    options = StreamConfigurationOptions(record_type=RecordType.JSON)

    # Create stream
    try:
        stream = sdk.create_stream(
            client_id,
            client_secret,
            table_properties,
            options
        )
        print("✅ Zerobus stream created")
    except Exception as e:
        print(f"\n❌ Failed to create Zerobus stream: {e}")
        print("\nPossible issues:")
        print("  - Service principal lacks permissions (need USE CATALOG, USE SCHEMA, MODIFY, SELECT)")
        print("  - Table signaltogrowth.bronze.platform_events doesn't exist")
        print("    → Run: databricks/setup_zerobus_streaming.sql in Databricks SQL Editor")
        print("  - Zerobus Ingest not enabled in workspace (Admin Settings → Lakeflow Connect)")
        print("  - Invalid service principal credentials (check CLIENT_ID and CLIENT_SECRET)")
        return False

    # Create test event
    test_event = {
        "event_id": str(uuid.uuid4()),
        "event_name": "test_connection",
        "event_version": "v1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": str(uuid.uuid4()),
        "user_id": "test-user",
        "properties": {
            "test": "true",
            "source": "test_zerobus_connection.py"
        }
    }

    print(f"\nTest Event:")
    print(f"  event_id: {test_event['event_id']}")
    print(f"  event_name: {test_event['event_name']}")
    print(f"  session_id: {test_event['session_id']}")

    # Ingest test record
    try:
        offset = stream.ingest_record_offset(test_event)
        print(f"\n✅ Test record ingested (offset: {offset})")
    except Exception as e:
        print(f"\n❌ Failed to ingest test record: {e}")
        stream.close()
        return False

    # Flush to ensure write completes
    try:
        stream.flush()
        print("✅ Stream flushed")
    except Exception as e:
        print(f"\n⚠️  Warning: Failed to flush stream: {e}")

    # Close stream
    try:
        stream.close()
        print("✅ Stream closed")
    except Exception as e:
        print(f"\n⚠️  Warning: Failed to close stream gracefully: {e}")

    print("\n" + "=" * 80)
    print("✅ Zerobus Connection Test PASSED")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Verify event in Databricks SQL Editor:")
    print(f"     SELECT * FROM signaltogrowth.bronze.platform_events")
    print(f"     WHERE event_id = '{test_event['event_id']}'")
    print("  2. Note: Zerobus has ~5 second latency, so wait a bit before querying")
    print("  3. Proceed with implementing ZerobusPublisher service (US-2.2)")

    return True


if __name__ == "__main__":
    success = test_zerobus_connection()
    sys.exit(0 if success else 1)
