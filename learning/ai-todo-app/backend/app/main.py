"""FastAPI main application.

Entry point for the AI Todo App backend.
Provides REST API for task management and AI agent interaction.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uuid
from datetime import datetime
from typing import Optional

from .config import settings
from .db import (
    async_test_connection,
    db_client,
    async_create_task,
    async_get_task_by_id,
    async_get_tasks_by_user,
    async_update_task,
    async_delete_task,
)
from .schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    ErrorResponse,
    TaskStatus,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup/shutdown)."""
    # Startup
    logger.info("Starting AI Todo App backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Databricks host: {settings.databricks_host}")

    # Test database connection on startup
    try:
        connection_status = await async_test_connection()
        if connection_status["status"] == "connected":
            logger.info("✓ Databricks connection successful")
        else:
            logger.error(f"✗ Databricks connection failed: {connection_status}")
    except Exception as e:
        logger.error(f"✗ Failed to test Databricks connection: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AI Todo App backend...")
    db_client.close()


# Initialize FastAPI app
app = FastAPI(
    title="AI Todo App API",
    description="Task management with AI agent powered by FastAPI, Databricks, and LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Todo App API",
        "version": "1.0.0",
        "environment": settings.environment,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with Databricks connection status."""
    try:
        connection_status = await async_test_connection()

        if connection_status["status"] == "connected":
            return {
                "status": "healthy",
                "database": "connected",
                "databricks": connection_status,
            }
        else:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": connection_status.get("error_message", "Unknown error"),
                },
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "error",
                "error": str(e),
            },
        )


# ============================================================================
# TASK CRUD ENDPOINTS
# ============================================================================


@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
async def create_task_endpoint(task: TaskCreate):
    """Create a new task.

    Returns:
        Created task with generated ID and timestamps
    """
    try:
        # Generate task ID and timestamps
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Create task in database
        created_task = await async_create_task(
            task_id=task_id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            due_date=task.due_date.isoformat() if task.due_date else None,
            created_at=now,
            updated_at=now,
        )

        if not created_task:
            raise HTTPException(status_code=500, detail="Failed to create task")

        return TaskResponse(**created_task)

    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def get_tasks_endpoint(
    user_id: str = Query(..., description="User ID to filter tasks"),
    status: Optional[TaskStatus] = Query(None, description="Optional status filter"),
):
    """Get all tasks for a user, optionally filtered by status.

    Returns:
        List of tasks matching the filters
    """
    try:
        tasks = await async_get_tasks_by_user(
            user_id=user_id,
            status=status.value if status else None
        )

        # Convert to TaskResponse objects
        task_responses = [TaskResponse(**task) for task in tasks]

        return TaskListResponse(tasks=task_responses, total=len(task_responses))

    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task_endpoint(task_id: str):
    """Get a single task by ID.

    Returns:
        Task details

    Raises:
        404: Task not found
    """
    try:
        task = await async_get_task_by_id(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return TaskResponse(**task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch task: {str(e)}")


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task_endpoint(task_id: str, task_update: TaskUpdate):
    """Update a task.

    Only provided fields will be updated.

    Returns:
        Updated task

    Raises:
        404: Task not found
    """
    try:
        # Check if task exists
        existing_task = await async_get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        # Build updates dict (only include provided fields)
        updates = {"updated_at": datetime.utcnow().isoformat()}

        if task_update.title is not None:
            updates["title"] = task_update.title
        if task_update.description is not None:
            updates["description"] = task_update.description
        if task_update.status is not None:
            updates["status"] = task_update.status.value
        if task_update.priority is not None:
            updates["priority"] = task_update.priority.value
        if task_update.due_date is not None:
            updates["due_date"] = task_update.due_date.isoformat()

        # Update task
        updated_task = await async_update_task(task_id, updates)

        if not updated_task:
            raise HTTPException(status_code=500, detail="Failed to update task")

        return TaskResponse(**updated_task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
async def delete_task_endpoint(task_id: str):
    """Delete a task.

    Returns:
        204 No Content on success

    Raises:
        404: Task not found
    """
    try:
        deleted = await async_delete_task(task_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

from .agent import process_agent_message, AgentResponse as AgentResponseSchema


@app.post("/agent/chat", response_model=AgentResponseSchema, tags=["Agent"])
async def agent_chat_endpoint(
    message: str = Query(..., description="User's natural language message"),
    user_id: str = Query(default="test-user-001", description="User ID"),
):
    """Process natural language message and create task.

    The AI agent extracts task details from the message and creates a task.

    Returns:
        Agent response with confirmation and task details

    Example:
        POST /agent/chat?message=Remind me to buy milk tomorrow&user_id=test-user-001
    """
    try:
        response = await process_agent_message(message, user_id)
        return response

    except Exception as e:
        logger.error(f"Error in agent chat: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
