"""Standalone AI Agent Service with OpenTelemetry instrumentation.

Simplified version that extracts tasks from natural language without saving to database.
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from opentelemetry import trace

# Load environment variables
load_dotenv()
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry
def setup_telemetry():
    """Configure OpenTelemetry with OTLP exporter."""
    resource = Resource(attributes={
        "service.name": "ai-agent",
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENV", "development")
    })

    provider = TracerProvider(resource=resource)

    # OTLP Exporter (sends to collector)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)

    logger.info(f"OpenTelemetry configured with OTLP endpoint: {otlp_endpoint}")

setup_telemetry()
tracer = trace.get_tracer(__name__)

# Initialize FastAPI
app = FastAPI(title="AI Agent Service", version="1.0.0")

# Initialize OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai_client = OpenAI(api_key=openai_api_key)


# Pydantic Models
class ProcessRequest(BaseModel):
    """Request to process a message."""
    message: str = Field(..., min_length=1, max_length=1000, description="User message to process")


class TaskExtraction(BaseModel):
    """Extracted task details."""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: str = Field(default="medium", description="Priority: low, medium, high, urgent")
    due_date_relative: Optional[str] = Field(None, description="Relative due date")
    confidence: float = Field(default=0.8, description="Confidence score 0-1")


class ProcessResponse(BaseModel):
    """Response from agent."""
    task: TaskExtraction
    message: str = Field(..., description="Human-readable response")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


def parse_relative_date(relative_str: str) -> Optional[datetime]:
    """Parse relative date strings."""
    if not relative_str:
        return None

    relative_str = relative_str.lower().strip()
    now = datetime.utcnow()

    if "tomorrow" in relative_str:
        return now + timedelta(days=1)
    if "today" in relative_str:
        return now
    if "next week" in relative_str:
        return now + timedelta(weeks=1)

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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-agent", "version": "1.0.0"}


@app.post("/process", response_model=ProcessResponse)
async def process_message(request: ProcessRequest):
    """Process user message and extract task details.

    This endpoint uses OpenAI to extract task information from natural language.
    Traces are sent to the OTLP collector for observability.
    """
    start_time = datetime.utcnow()

    with tracer.start_as_current_span(
        "agent.process_message",
        attributes={
            "message_length": len(request.message),
        }
    ) as span:
        try:
            logger.info(f"Processing message: {request.message}")

            # Extract task using OpenAI
            with tracer.start_as_current_span("agent.extract_task") as extract_span:
                system_prompt = """You are a task extraction assistant. Extract task details from user messages.

Extract:
- title: Concise task title (required)
- description: Additional details (optional)
- priority: Infer from urgency words (urgent/asap → urgent, important → high, otherwise → medium)
- due_date_relative: Extract dates like "tomorrow", "in 2 days", "next week"
- confidence: Your confidence in the extraction (0.0 to 1.0)

Examples:
- "Buy milk tomorrow" → title: "Buy milk", due_date_relative: "tomorrow", confidence: 0.9
- "URGENT: Fix production bug" → title: "Fix production bug", priority: "urgent", confidence: 0.95
- "Call mom" → title: "Call mom", confidence: 0.85

Return valid JSON only."""

                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )

                content = response.choices[0].message.content
                data = json.loads(content)

                # Add GenAI semantic conventions
                usage = response.usage
                if usage:
                    extract_span.set_attribute("gen_ai.request.model", "gpt-4o-mini")
                    extract_span.set_attribute("gen_ai.usage.input_tokens", usage.prompt_tokens)
                    extract_span.set_attribute("gen_ai.usage.output_tokens", usage.completion_tokens)
                    extract_span.set_attribute("gen_ai.usage.total_tokens", usage.total_tokens)

                if response.choices:
                    extract_span.set_attribute("gen_ai.response.finish_reason", response.choices[0].finish_reason)

                extraction = TaskExtraction(**data)

                extract_span.set_attribute("extraction.priority", extraction.priority)
                extract_span.set_attribute("extraction.confidence", extraction.confidence)
                extract_span.set_attribute("extraction.has_due_date", bool(extraction.due_date_relative))

            # Parse due date if provided
            due_date = None
            if extraction.due_date_relative:
                due_date = parse_relative_date(extraction.due_date_relative)

            # Build response message
            response_parts = [f"✓ Extracted task: **{extraction.title}**"]
            if extraction.description:
                response_parts.append(f"Description: {extraction.description}")
            if extraction.priority in ["high", "urgent"]:
                response_parts.append(f"Priority: {extraction.priority}")
            if due_date:
                response_parts.append(f"Due: {due_date.strftime('%Y-%m-%d')}")

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            span.set_attribute("agent.success", True)
            span.set_attribute("agent.processing_time_ms", processing_time)

            return ProcessResponse(
                task=extraction,
                message="\n".join(response_parts),
                processing_time_ms=processing_time
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            span.record_exception(e)
            span.set_attribute("agent.success", False)
            raise HTTPException(status_code=500, detail="Failed to parse LLM response")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            span.record_exception(e)
            span.set_attribute("agent.success", False)
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
