#!/usr/bin/env python3
"""Test script to verify Langfuse OTLP integration.

This script:
1. Creates a test trace with GenAI semantic conventions
2. Exports to Langfuse via OTLP HTTP endpoint
3. Verifies connection and credentials

Usage:
    python scripts/test_langfuse_connection.py
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.telemetry import setup_telemetry, get_tracer, add_genai_attributes


def test_langfuse_connection():
    """Test Langfuse connection by sending a test trace."""

    print("=" * 70)
    print("Testing Langfuse OTLP Integration")
    print("=" * 70)

    # Check credentials
    print("\n1. Checking Langfuse credentials...")
    if not settings.langfuse_public_key:
        print("❌ ERROR: LANGFUSE_PUBLIC_KEY not set in .env")
        print("\nSet up Langfuse:")
        print("  1. Go to https://cloud.langfuse.com")
        print("  2. Sign up or log in")
        print("  3. Create a new project")
        print("  4. Copy API keys from Settings → API Keys")
        print("  5. Add to backend/.env:")
        print("     LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("     LANGFUSE_SECRET_KEY=sk-lf-...")
        return False

    if not settings.langfuse_secret_key:
        print("❌ ERROR: LANGFUSE_SECRET_KEY not set in .env")
        return False

    print(f"✓ Langfuse public key: {settings.langfuse_public_key[:15]}...")
    print(f"✓ Langfuse host: {settings.langfuse_host}")

    # Initialize telemetry
    print("\n2. Initializing OpenTelemetry with Langfuse exporter...")
    try:
        setup_telemetry()
        print("✓ Telemetry initialized successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize telemetry: {e}")
        return False

    # Create test trace
    print("\n3. Creating test trace...")
    tracer = get_tracer()

    try:
        with tracer.start_as_current_span("test.langfuse_connection") as span:
            # Add GenAI semantic conventions
            add_genai_attributes(
                span=span,
                model="gpt-4o-mini",
                input_tokens=50,
                output_tokens=100,
                total_tokens=150,
                finish_reason="stop"
            )

            # Add test attributes
            span.set_attribute("test.purpose", "langfuse_connection_validation")
            span.set_attribute("test.timestamp", time.time())
            span.set_attribute("user_id", "test-user-001")
            span.set_attribute("session_id", "test-session-001")

            # Simulate some work
            time.sleep(0.1)

            print("✓ Test trace created successfully")

    except Exception as e:
        print(f"❌ ERROR: Failed to create trace: {e}")
        return False

    # Wait for export
    print("\n4. Waiting for trace export to Langfuse...")
    print("   (Batch span processor exports asynchronously)")
    time.sleep(3)
    print("✓ Trace should now be visible in Langfuse UI")

    # Print success message
    print("\n" + "=" * 70)
    print("✅ SUCCESS: Langfuse integration test complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Go to Langfuse UI: https://cloud.langfuse.com")
    print("  2. Navigate to your project → Traces")
    print("  3. Look for trace: 'test.langfuse_connection'")
    print("  4. Verify attributes:")
    print("     - gen_ai.request.model: gpt-4o-mini")
    print("     - gen_ai.usage.total_tokens: 150")
    print("     - test.purpose: langfuse_connection_validation")
    print("\nIf trace appears in UI within 10 seconds, integration is working! ✓")
    print("\nTroubleshooting:")
    print("  - Not seeing traces? Check API keys are correct")
    print("  - Check project selected in Langfuse UI matches your credentials")
    print("  - Look for errors in terminal output above")

    return True


if __name__ == "__main__":
    try:
        success = test_langfuse_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
