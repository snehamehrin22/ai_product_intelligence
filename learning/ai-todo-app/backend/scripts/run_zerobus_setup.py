#!/usr/bin/env python3
"""
Execute Zerobus setup SQL script via Databricks SQL connector.

This script reads setup_zerobus_streaming.sql and executes it against Databricks.
"""

import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from databricks import sql

# Load environment variables
load_dotenv()


def execute_sql_file(sql_file_path: str):
    """Execute SQL statements from a file."""

    print("=" * 80)
    print("Executing Zerobus Setup SQL")
    print("=" * 80)

    # Read SQL file
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()

    # Connect to Databricks
    print("\n📡 Connecting to Databricks...")
    connection = sql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST").replace("https://", "").rstrip("/"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )

    cursor = connection.cursor()
    print("✅ Connected to Databricks SQL Warehouse")

    # Split SQL into statements (split on semicolon, but ignore comments)
    statements = []
    current_stmt = []

    for line in sql_content.split('\n'):
        # Skip comment-only lines
        stripped = line.strip()
        if stripped.startswith('--') or not stripped:
            continue

        current_stmt.append(line)

        # If line ends with semicolon, it's end of statement
        if stripped.endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_stmt = []

    print(f"\n📝 Found {len(statements)} SQL statements to execute\n")

    # Execute each statement
    success_count = 0
    error_count = 0

    for i, stmt in enumerate(statements, 1):
        # Get first line for display (truncate if too long)
        first_line = stmt.split('\n')[0]
        if len(first_line) > 70:
            first_line = first_line[:67] + "..."

        print(f"[{i}/{len(statements)}] {first_line}")

        try:
            cursor.execute(stmt)

            # For queries that return results (SELECT, SHOW, DESCRIBE)
            if stmt.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                results = cursor.fetchall()
                if results:
                    print(f"      → Returned {len(results)} rows")
                    # Show first few rows for verification queries
                    if 'COUNT' in stmt.upper():
                        for row in results[:3]:
                            print(f"         {row}")
            else:
                print("      ✅ Success")

            success_count += 1

        except Exception as e:
            error_msg = str(e)
            # Some errors are expected (like "already exists" for idempotent scripts)
            if 'already exists' in error_msg.lower():
                print(f"      ⚠️  Already exists (skipping)")
                success_count += 1
            else:
                print(f"      ❌ Error: {error_msg}")
                error_count += 1

        print()

    cursor.close()
    connection.close()

    # Summary
    print("=" * 80)
    if error_count == 0:
        print(f"✅ Setup Complete! ({success_count}/{len(statements)} statements executed)")
    else:
        print(f"⚠️  Setup Completed with Errors ({success_count} success, {error_count} errors)")
    print("=" * 80)

    print("\nNext steps:")
    print("  1. Run: python scripts/test_zerobus_connection.py")
    print("  2. Verify test event in Databricks:")
    print("     SELECT * FROM signaltogrowth.bronze.platform_events LIMIT 10;")

    return error_count == 0


if __name__ == "__main__":
    sql_file = Path(__file__).parent.parent.parent / "databricks" / "setup_zerobus_streaming.sql"

    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)

    success = execute_sql_file(str(sql_file))
    sys.exit(0 if success else 1)
