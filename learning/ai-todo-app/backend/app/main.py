"""FastAPI main application.

Entry point for the AI Todo App backend.
Provides REST API for task management and AI agent interaction.
"""

from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uuid
from datetime import datetime
from typing import Optional

from .config import settings
from .events import get_zerobus_publisher, ZerobusPublisher
from .event_schemas.events import (
    TaskCreatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
)
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
async def create_task_endpoint(
    task: TaskCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    publisher: ZerobusPublisher = Depends(get_zerobus_publisher)
):
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

        # Extract session_id from headers (or generate if missing)
        session_id = request.headers.get('X-Session-Id', str(uuid.uuid4()))

        # Emit task_created event (fire-and-forget)
        background_tasks.add_task(
            publisher.publish,
            {
                "event_name": "task_created",
                "session_id": session_id,
                "user_id": task.user_id,
                "properties": {
                    "task_id": task_id,
                    "title": task.title,
                    "description": task.description or "",
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
            },
            table="platform_events"
        )

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
async def update_task_endpoint(
    task_id: str,
    task_update: TaskUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    publisher: ZerobusPublisher = Depends(get_zerobus_publisher)
):
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
        updated_fields = []
        previous_values = {}
        current_values = {}

        if task_update.title is not None:
            updates["title"] = task_update.title
            updated_fields.append("title")
            previous_values["title"] = existing_task["title"]
            current_values["title"] = task_update.title
        if task_update.description is not None:
            updates["description"] = task_update.description
            updated_fields.append("description")
            previous_values["description"] = existing_task.get("description")
            current_values["description"] = task_update.description
        if task_update.status is not None:
            updates["status"] = task_update.status.value
            updated_fields.append("status")
            previous_values["status"] = existing_task["status"]
            current_values["status"] = task_update.status.value
        if task_update.priority is not None:
            updates["priority"] = task_update.priority.value
            updated_fields.append("priority")
            previous_values["priority"] = existing_task["priority"]
            current_values["priority"] = task_update.priority.value
        if task_update.due_date is not None:
            updates["due_date"] = task_update.due_date.isoformat()
            updated_fields.append("due_date")
            previous_values["due_date"] = existing_task.get("due_date")
            current_values["due_date"] = task_update.due_date.isoformat()

        # Update task
        updated_task = await async_update_task(task_id, updates)

        if not updated_task:
            raise HTTPException(status_code=500, detail="Failed to update task")

        # Extract session_id from headers (or generate if missing)
        session_id = request.headers.get('X-Session-Id', str(uuid.uuid4()))

        # Emit task_updated event (fire-and-forget)
        background_tasks.add_task(
            publisher.publish,
            {
                "event_name": "task_updated",
                "session_id": session_id,
                "user_id": existing_task["user_id"],
                "properties": {
                    "task_id": task_id,
                    "title": updated_task["title"],
                    "updated_fields": updated_fields,
                    "previous_values": previous_values,
                    "current_values": current_values
                }
            },
            table="platform_events"
        )

        return TaskResponse(**updated_task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
async def delete_task_endpoint(
    task_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    publisher: ZerobusPublisher = Depends(get_zerobus_publisher)
):
    """Delete a task.

    Returns:
        204 No Content on success

    Raises:
        404: Task not found
    """
    try:
        # Get task before deletion (for event properties)
        existing_task = await async_get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        # Delete task
        deleted = await async_delete_task(task_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        # Extract session_id from headers (or generate if missing)
        session_id = request.headers.get('X-Session-Id', str(uuid.uuid4()))

        # Emit task_deleted event (fire-and-forget)
        background_tasks.add_task(
            publisher.publish,
            {
                "event_name": "task_deleted",
                "session_id": session_id,
                "user_id": existing_task["user_id"],
                "properties": {
                    "task_id": task_id,
                    "title": existing_task["title"],
                    "status": existing_task["status"]
                }
            },
            table="platform_events"
        )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


@app.patch("/tasks/{task_id}/complete", response_model=TaskResponse, tags=["Tasks"])
async def toggle_task_completion_endpoint(
    task_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    publisher: ZerobusPublisher = Depends(get_zerobus_publisher)
):
    """Toggle task completion status.

    If task is not completed, marks it as completed.
    If task is completed, marks it as pending.

    Returns:
        Updated task

    Raises:
        404: Task not found
    """
    try:
        # Get current task
        existing_task = await async_get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        # Determine new status (toggle between completed and pending)
        current_status = existing_task["status"]
        new_status = "completed" if current_status != "completed" else "pending"

        # Update task status
        updates = {
            "status": new_status,
            "updated_at": datetime.utcnow().isoformat()
        }
        updated_task = await async_update_task(task_id, updates)

        if not updated_task:
            raise HTTPException(status_code=500, detail="Failed to update task")

        # Extract session_id from headers (or generate if missing)
        session_id = request.headers.get('X-Session-Id', str(uuid.uuid4()))

        # Emit task_completed event only when transitioning TO completed status
        if new_status == "completed":
            background_tasks.add_task(
                publisher.publish,
                {
                    "event_name": "task_completed",
                    "session_id": session_id,
                    "user_id": existing_task["user_id"],
                    "properties": {
                        "task_id": task_id,
                        "title": existing_task["title"],
                        "previous_status": current_status,
                        "completed_at": updates["updated_at"]
                    }
                },
                table="platform_events"
            )

        return TaskResponse(**updated_task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling task completion {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle task completion: {str(e)}")


# ============================================================================
# PLATFORM EVENTS API ENDPOINT
# ============================================================================

from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError


class EventBatch(BaseModel):
    """Batch of platform events from frontend."""
    events: List[Dict[str, Any]]


@app.post("/events", status_code=202, tags=["Events"])
async def receive_platform_events_endpoint(
    event_batch: EventBatch,
    request: Request,
    background_tasks: BackgroundTasks,
    publisher: ZerobusPublisher = Depends(get_zerobus_publisher)
):
    """Receive platform events from frontend and publish to Zerobus.

    Accepts batch of events, validates them, and publishes to Delta Lake via Zerobus.

    Returns:
        202 Accepted - Events are being processed asynchronously

    Example:
        POST /events
        Headers: X-Session-Id: session-uuid
        Body: {
            "events": [
                {
                    "event_name": "page_viewed",
                    "user_id": "user-123",
                    "properties": {"page": "/tasks"}
                }
            ]
        }
    """
    try:
        # Extract session_id from headers (or generate if missing)
        session_id = request.headers.get('X-Session-Id', str(uuid.uuid4()))

        # Validate batch size (max 100 events)
        if len(event_batch.events) > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size exceeds maximum of 100 events"
            )

        # Merge session_id into each event if not present
        processed_events = []
        validation_errors = []

        for idx, event in enumerate(event_batch.events):
            try:
                # Add session_id if missing
                if 'session_id' not in event:
                    event['session_id'] = session_id

                # Validate required fields
                if 'event_name' not in event:
                    validation_errors.append({
                        "index": idx,
                        "error": "Missing required field: event_name"
                    })
                    continue

                if 'user_id' not in event:
                    validation_errors.append({
                        "index": idx,
                        "error": "Missing required field: user_id"
                    })
                    continue

                processed_events.append(event)

            except Exception as e:
                validation_errors.append({
                    "index": idx,
                    "error": f"Validation error: {str(e)}"
                })
                logger.warning(f"Event validation failed at index {idx}: {e}")

        # Publish valid events in background (fire-and-forget)
        if processed_events:
            for event in processed_events:
                background_tasks.add_task(
                    publisher.publish,
                    event,
                    table="platform_events"
                )

            logger.info(f"Accepted {len(processed_events)} events for processing (session: {session_id})")

        # Return 202 Accepted with summary
        response_data = {
            "status": "accepted",
            "total_events": len(event_batch.events),
            "accepted_events": len(processed_events),
            "rejected_events": len(validation_errors),
            "session_id": session_id
        }

        if validation_errors:
            response_data["validation_errors"] = validation_errors

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing event batch: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process events: {str(e)}"
        )


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
