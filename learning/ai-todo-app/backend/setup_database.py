"""Database setup script - Execute schema SQL in Databricks.

This script reads the setup_schema.sql file and executes each statement
in Databricks to create tables and insert test data.

Usage:
    python setup_database.py
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import db_client


def execute_sql_file(sql_file_path: str):
    """Execute SQL statements from a file.

    Args:
        sql_file_path: Path to SQL file
    """
    print(f"Reading SQL file: {sql_file_path}")

    with open(sql_file_path, 'r') as f:
        sql_content = f.read()

    # Split by semicolon and filter out comments/empty lines
    statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        # Skip pure comment lines and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('--'):
            continue

        current_statement.append(line)

        # If line ends with semicolon, it's end of statement
        if stripped.endswith(';'):
            statement = '\n'.join(current_statement).strip()
            if statement and not statement.startswith('--'):
                statements.append(statement)
            current_statement = []

    print(f"\nFound {len(statements)} SQL statements to execute\n")

    # Execute each statement
    for i, statement in enumerate(statements, 1):
        # Show first 80 chars of statement
        preview = statement.replace('\n', ' ')[:80]
        print(f"[{i}/{len(statements)}] Executing: {preview}...")

        try:
            db_client.execute_command(statement, commit=True)
            print("✓ Success\n")
        except Exception as e:
            error_msg = str(e)
            # Some statements might fail if already exists - that's OK
            if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                print(f"⚠ Already exists (skipping): {error_msg}\n")
            else:
                print(f"✗ Error: {error_msg}\n")
                raise


def verify_setup():
    """Verify tables were created successfully."""
    print("=" * 80)
    print("VERIFYING SETUP")
    print("=" * 80)

    # Check users table
    print("\n1. Checking users table...")
    try:
        users = db_client.execute_query("SELECT * FROM signaltogrowth.todo_app.users")
        print(f"✓ Users table exists with {len(users)} rows")
        for user in users:
            print(f"  - {user.get('email')} ({user.get('full_name')})")
    except Exception as e:
        print(f"✗ Error querying users: {e}")
        raise

    # Check tasks table
    print("\n2. Checking tasks table...")
    try:
        tasks = db_client.execute_query("SELECT * FROM signaltogrowth.todo_app.tasks ORDER BY created_at")
        print(f"✓ Tasks table exists with {len(tasks)} rows")
        for task in tasks:
            print(f"  - [{task.get('status')}] {task.get('title')}")
    except Exception as e:
        print(f"✗ Error querying tasks: {e}")
        raise

    print("\n" + "=" * 80)
    print("✓ DATABASE SETUP COMPLETE")
    print("=" * 80)


def main():
    """Main setup function."""
    print("=" * 80)
    print("AI TODO APP - DATABASE SETUP")
    print("=" * 80)

    # Get SQL file path
    backend_dir = Path(__file__).parent
    project_dir = backend_dir.parent
    sql_file = project_dir / "databricks" / "setup_schema.sql"

    if not sql_file.exists():
        print(f"✗ Error: SQL file not found at {sql_file}")
        sys.exit(1)

    try:
        # Execute SQL file
        execute_sql_file(str(sql_file))

        # Verify setup
        verify_setup()

        print("\n✓ All done! Your database is ready.")

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
