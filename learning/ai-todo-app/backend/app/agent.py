"""AI Agent for natural language task creation using LangGraph and OpenAI.

The agent extracts task details from natural language input and creates tasks.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re

from openai import OpenAI
from pydantic import BaseModel, Field

from .config import settings
from .db import async_create_task
from .schemas import TaskStatus, TaskPriority
from .telemetry import get_tracer, add_genai_attributes

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)


class TaskExtraction(BaseModel):
    """Schema for extracted task details from natural language."""

    title: str = Field(..., description="Task title extracted from user message")
    description: Optional[str] = Field(None, description="Detailed description if provided")
    priority: str = Field(default="medium", description="Task priority: low, medium, high, urgent")
    due_date_relative: Optional[str] = Field(None, description="Relative due date like 'tomorrow', 'in 2 days', 'next week'")
    due_date_absolute: Optional[str] = Field(None, description="Absolute due date in YYYY-MM-DD format")


class AgentResponse(BaseModel):
    """Agent response to user."""

    message: str = Field(..., description="Response message to user")
    task_created: bool = Field(..., description="Whether a task was created")
    task_id: Optional[str] = Field(None, description="Created task ID if applicable")
    needs_clarification: bool = Field(default=False, description="Whether agent needs more info")


def parse_relative_date(relative_str: str) -> Optional[datetime]:
    """Parse relative date strings like 'tomorrow', 'in 2 days', 'next week'.

    Args:
        relative_str: Relative date string

    Returns:
        Datetime object or None
    """
    if not relative_str:
        return None

    relative_str = relative_str.lower().strip()
    now = datetime.utcnow()

    # Tomorrow
    if "tomorrow" in relative_str:
        return now + timedelta(days=1)

    # Today
    if "today" in relative_str:
        return now

    # Next week
    if "next week" in relative_str:
        return now + timedelta(weeks=1)

    # In X days/hours
    match = re.search(r'in\s+(\d+)\s+(day|hour|week)s?', relative_str)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit == "day":
            return now + timedelta(days=amount)
        elif unit == "hour":
            return now + timedelta(hours=amount)
        elif unit == "week":
            return now + timedelta(weeks=amount)

    return None


async def extract_task_from_message(user_message: str, user_id: str) -> TaskExtraction:
    """Extract task details from natural language using OpenAI.

    Args:
        user_message: User's natural language input
        user_id: User ID creating the task

    Returns:
        Extracted task details
    """
    tracer = get_tracer()

    with tracer.start_as_current_span(
        "agent.extract_task",
        attributes={
            "user_id": user_id,
            "message_length": len(user_message),
        }
    ) as span:
        system_prompt = """You are a helpful task extraction assistant. Extract task details from user messages.

Extract the following:
- title: A concise task title (required)
- description: Additional details if provided (optional)
- priority: Infer from words like "urgent", "important", "asap" → high/urgent, otherwise medium
- due_date_relative: Extract relative dates like "tomorrow", "in 2 days", "next week"
- due_date_absolute: Extract absolute dates in YYYY-MM-DD format if provided

Examples:
- "Remind me to buy milk tomorrow" → title: "Buy milk", due_date_relative: "tomorrow"
- "Schedule dentist appointment next week at 3pm" → title: "Schedule dentist appointment", due_date_relative: "next week"
- "URGENT: Fix production bug ASAP" → title: "Fix production bug", priority: "urgent"
- "Call mom" → title: "Call mom"

Return valid JSON only."""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=500
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            # Add GenAI semantic conventions
            usage = response.usage
            add_genai_attributes(
                span,
                model="gpt-4o-mini",
                input_tokens=usage.prompt_tokens if usage else None,
                output_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None,
                finish_reason=response.choices[0].finish_reason if response.choices else None
            )

            span.set_attribute("extraction.has_description", bool(data.get("description")))
            span.set_attribute("extraction.priority", data.get("priority", "medium"))

            return TaskExtraction(**data)

        except Exception as e:
            logger.error(f"Error extracting task: {e}")
            span.record_exception(e)
            # Fallback: use the entire message as title
            return TaskExtraction(
                title=user_message[:200],  # Max title length
                description=None,
                priority="medium"
            )


async def process_agent_message(user_message: str, user_id: str = "test-user-001") -> AgentResponse:
    """Process user message and create task if applicable.

    Args:
        user_message: User's natural language input
        user_id: User ID (default: test-user-001)

    Returns:
        Agent response
    """
    tracer = get_tracer()

    with tracer.start_as_current_span(
        "agent.process_message",
        attributes={
            "user_id": user_id,
            "message_length": len(user_message),
        }
    ) as span:
        try:
            logger.info(f"Processing agent message: {user_message}")

            # Extract task details using OpenAI
            extraction = await extract_task_from_message(user_message, user_id)

            logger.info(f"Extracted task: {extraction}")

            # Parse due date
            due_date = None
            if extraction.due_date_absolute:
                try:
                    due_date = datetime.fromisoformat(extraction.due_date_absolute)
                except ValueError:
                    pass
            elif extraction.due_date_relative:
                due_date = parse_relative_date(extraction.due_date_relative)

            # Validate priority
            priority = extraction.priority.lower()
            if priority not in ["low", "medium", "high", "urgent"]:
                priority = "medium"

            # Create task
            import uuid
            task_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            created_task = await async_create_task(
                task_id=task_id,
                user_id=user_id,
                title=extraction.title,
                description=extraction.description,
                status=TaskStatus.PENDING.value,
                priority=priority,
                due_date=due_date.isoformat() if due_date else None,
                created_at=now,
                updated_at=now
            )

            if not created_task:
                span.set_attribute("agent.task_created", False)
                return AgentResponse(
                    message="Sorry, I couldn't create the task. Please try again.",
                    task_created=False,
                    needs_clarification=False
                )

            # Add trace attributes
            span.set_attribute("agent.task_created", True)
            span.set_attribute("agent.task_id", task_id)
            span.set_attribute("agent.task_priority", priority)

            # Build response message
            response_parts = [f"✓ Created task: **{extraction.title}**"]

            if extraction.description:
                response_parts.append(f"Description: {extraction.description}")

            if priority in ["high", "urgent"]:
                response_parts.append(f"Priority: {priority}")

            if due_date:
                response_parts.append(f"Due: {due_date.strftime('%Y-%m-%d %H:%M')}")

            return AgentResponse(
                message="\n".join(response_parts),
                task_created=True,
                task_id=task_id,
                needs_clarification=False
            )

        except Exception as e:
            logger.error(f"Error processing agent message: {e}")
            span.record_exception(e)
            return AgentResponse(
                message=f"Sorry, I encountered an error: {str(e)}",
                task_created=False,
                needs_clarification=False
            )
