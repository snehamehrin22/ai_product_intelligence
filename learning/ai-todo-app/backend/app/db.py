"""Database connection and query functions for Databricks.

Uses Databricks SQL Connector (synchronous) wrapped in asyncio.to_thread() for FastAPI.

Key Pattern:
- Databricks is used as OLTP database (Lakebase pattern), not just analytics
- Delta Lake provides ACID transactions
- All queries use Unity Catalog: {catalog}.{schema}.{table}
"""

import asyncio
from typing import Optional
from databricks import sql
from databricks.sql.client import Connection, Cursor
from .config import settings


class DatabricksClient:
    """Manages Databricks SQL connection and queries."""

    def __init__(self):
        """Initialize client (connection created on demand)."""
        self._connection: Optional[Connection] = None

    def _get_connection(self) -> Connection:
        """Get or create database connection.

        Note: This is a synchronous operation. Caller should wrap in asyncio.to_thread()
        when calling from async FastAPI routes.
        """
        if self._connection is None or not self._is_connection_healthy():
            self._connection = sql.connect(
                server_hostname=settings.databricks_host.replace("https://", ""),
                http_path=settings.databricks_http_path,
                access_token=settings.databricks_token,
            )
        return self._connection

    def _is_connection_healthy(self) -> bool:
        """Check if connection is still alive."""
        if self._connection is None:
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception:
            return False

    def test_connection(self) -> dict:
        """Test Databricks connection with a simple query.

        Returns:
            dict: Connection status with details

        Raises:
            Exception: If connection fails
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            cursor.close()

            return {
                "status": "connected",
                "databricks_host": settings.databricks_host,
                "catalog": settings.databricks_catalog,
                "schema": settings.databricks_schema,
                "test_query_result": result[0] if result else None,
            }
        except Exception as e:
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "databricks_host": settings.databricks_host,
            }

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list[dict]:
        """Execute a SELECT query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            columns = [desc[0] for desc in cursor.description or []]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()

    def execute_command(
        self, command: str, params: Optional[tuple] = None, commit: bool = True
    ) -> int:
        """Execute an INSERT/UPDATE/DELETE command.

        Args:
            command: SQL command string
            params: Optional command parameters
            commit: Whether to commit after execution

        Returns:
            Number of rows affected
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(command, params or ())
            if commit:
                conn.commit()
            # Databricks doesn't support rowcount reliably, so we return 1 on success
            return 1
        finally:
            cursor.close()

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


# Global database client instance
db_client = DatabricksClient()


# Async wrappers for FastAPI routes
async def async_test_connection() -> dict:
    """Async wrapper for test_connection."""
    return await asyncio.to_thread(db_client.test_connection)


async def async_execute_query(query: str, params: Optional[tuple] = None) -> list[dict]:
    """Async wrapper for execute_query."""
    return await asyncio.to_thread(db_client.execute_query, query, params)


async def async_execute_command(
    command: str, params: Optional[tuple] = None, commit: bool = True
) -> int:
    """Async wrapper for execute_command."""
    return await asyncio.to_thread(db_client.execute_command, command, params, commit)


# ============================================================================
# TASK CRUD OPERATIONS
# ============================================================================


def create_task(
    task_id: str,
    user_id: str,
    title: str,
    description: Optional[str],
    status: str,
    priority: str,
    due_date: Optional[str],
    created_at: str,
    updated_at: str
) -> dict:
    """Create a new task in the database.

    Args:
        task_id: Unique task identifier
        user_id: User who owns the task
        title: Task title
        description: Task description (optional)
        status: Task status (pending, in_progress, completed, cancelled)
        priority: Task priority (low, medium, high, urgent)
        due_date: Due date/time as ISO string (optional)
        created_at: Creation timestamp as ISO string
        updated_at: Update timestamp as ISO string

    Returns:
        Created task as dict
    """
    conn = db_client._get_connection()
    cursor = conn.cursor()
    try:
        # Insert task
        sql = """
        INSERT INTO signaltogrowth.todo_app.tasks
        (task_id, user_id, title, description, status, priority, due_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (task_id, user_id, title, description, status, priority, due_date, created_at, updated_at))
        conn.commit()

        # Retrieve the created task
        cursor.execute("SELECT * FROM signaltogrowth.todo_app.tasks WHERE task_id = ?", (task_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None
    finally:
        cursor.close()


def get_task_by_id(task_id: str) -> Optional[dict]:
    """Get a task by its ID.

    Args:
        task_id: Task identifier

    Returns:
        Task as dict or None if not found
    """
    results = db_client.execute_query(
        "SELECT * FROM signaltogrowth.todo_app.tasks WHERE task_id = ?",
        (task_id,)
    )
    return results[0] if results else None


def get_tasks_by_user(user_id: str, status: Optional[str] = None) -> list[dict]:
    """Get all tasks for a user, optionally filtered by status.

    Args:
        user_id: User identifier
        status: Optional status filter

    Returns:
        List of tasks
    """
    if status:
        return db_client.execute_query(
            "SELECT * FROM signaltogrowth.todo_app.tasks WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
            (user_id, status)
        )
    else:
        return db_client.execute_query(
            "SELECT * FROM signaltogrowth.todo_app.tasks WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )


def update_task(task_id: str, updates: dict) -> Optional[dict]:
    """Update a task with the provided fields.

    Args:
        task_id: Task identifier
        updates: Dict of fields to update (must include updated_at)

    Returns:
        Updated task as dict or None if not found
    """
    if not updates:
        return get_task_by_id(task_id)

    # Build UPDATE statement dynamically
    set_clauses = []
    values = []
    for key, value in updates.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)

    values.append(task_id)  # For WHERE clause

    sql = f"""
    UPDATE signaltogrowth.todo_app.tasks
    SET {", ".join(set_clauses)}
    WHERE task_id = ?
    """

    conn = db_client._get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, tuple(values))
        conn.commit()

        # Return updated task
        return get_task_by_id(task_id)
    finally:
        cursor.close()


def delete_task(task_id: str) -> bool:
    """Delete a task by its ID.

    Args:
        task_id: Task identifier

    Returns:
        True if deleted, False if not found
    """
    # Check if task exists
    if not get_task_by_id(task_id):
        return False

    db_client.execute_command(
        "DELETE FROM signaltogrowth.todo_app.tasks WHERE task_id = ?",
        (task_id,),
        commit=True
    )
    return True


# Async wrappers for CRUD operations
async def async_create_task(*args, **kwargs) -> dict:
    """Async wrapper for create_task."""
    return await asyncio.to_thread(create_task, *args, **kwargs)


async def async_get_task_by_id(task_id: str) -> Optional[dict]:
    """Async wrapper for get_task_by_id."""
    return await asyncio.to_thread(get_task_by_id, task_id)


async def async_get_tasks_by_user(user_id: str, status: Optional[str] = None) -> list[dict]:
    """Async wrapper for get_tasks_by_user."""
    return await asyncio.to_thread(get_tasks_by_user, user_id, status)


async def async_update_task(task_id: str, updates: dict) -> Optional[dict]:
    """Async wrapper for update_task."""
    return await asyncio.to_thread(update_task, task_id, updates)


async def async_delete_task(task_id: str) -> bool:
    """Async wrapper for delete_task."""
    return await asyncio.to_thread(delete_task, task_id)
