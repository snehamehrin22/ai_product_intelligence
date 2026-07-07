"""OpenTelemetry instrumentation for AI Todo App.

Provides:
- Tracer configuration for LangGraph agent
- GenAI semantic conventions
- Langfuse integration for real-time trace visualization
- Session ID propagation via baggage
"""

import logging
from typing import Optional
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

from .config import settings

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[trace.Tracer] = None


def setup_telemetry():
    """Initialize OpenTelemetry instrumentation with Langfuse integration.

    This function should be called once during application startup.
    """
    global _tracer

    if _tracer is not None:
        logger.warning("Telemetry already initialized")
        return _tracer

    try:
        # Create resource with service name
        resource = Resource(attributes={
            SERVICE_NAME: "ai-todo-app-backend",
            "service.version": "1.0.0",
            "deployment.environment": settings.environment
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add Langfuse OTLP exporter if configured
        if hasattr(settings, 'langfuse_public_key') and settings.langfuse_public_key:
            logger.info("Configuring Langfuse OTLP exporter...")

            # Langfuse uses OTLP HTTP endpoint: https://cloud.langfuse.com/api/public/otel
            langfuse_host = getattr(settings, 'langfuse_host', 'https://cloud.langfuse.com')
            otlp_endpoint = f"{langfuse_host}/api/public/otel"

            # Configure OTLP exporter with Langfuse auth headers
            langfuse_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                headers={
                    "Authorization": f"Bearer {settings.langfuse_public_key}:{settings.langfuse_secret_key}"
                }
            )
            provider.add_span_processor(BatchSpanProcessor(langfuse_exporter))
            logger.info(f"✓ Langfuse OTLP exporter configured (endpoint: {otlp_endpoint})")
        else:
            logger.warning("Langfuse credentials not found - traces will not be sent to Langfuse")

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Auto-instrument OpenAI client
        OpenAIInstrumentor().instrument()
        logger.info("✓ OpenAI auto-instrumentation enabled")

        # Create tracer
        _tracer = trace.get_tracer(__name__)
        logger.info("✓ OpenTelemetry telemetry initialized")

        return _tracer

    except Exception as e:
        logger.error(f"Failed to initialize telemetry: {e}")
        # Return no-op tracer to prevent crashes
        return trace.get_tracer(__name__)


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance.

    Returns:
        Tracer instance (initializes if not already done)
    """
    global _tracer
    if _tracer is None:
        _tracer = setup_telemetry()
    return _tracer


def set_session_id(session_id: str):
    """Set session ID in baggage for propagation across traces.

    Args:
        session_id: Session UUID to attach to all spans
    """
    baggage.set_baggage("session_id", session_id)


def get_session_id() -> Optional[str]:
    """Get session ID from baggage.

    Returns:
        Session ID if set, None otherwise
    """
    return baggage.get_baggage("session_id")


def trace_agent_execution(func):
    """Decorator to trace agent function execution with GenAI conventions.

    Usage:
        @trace_agent_execution
        async def process_agent_message(message: str, user_id: str):
            ...

    Args:
        func: Async function to trace

    Returns:
        Wrapped function with tracing
    """
    async def wrapper(*args, **kwargs):
        tracer = get_tracer()

        # Extract message and user_id from args/kwargs
        message = args[0] if len(args) > 0 else kwargs.get('message', 'unknown')
        user_id = args[1] if len(args) > 1 else kwargs.get('user_id', 'unknown')

        with tracer.start_as_current_span(
            f"agent.{func.__name__}",
            attributes={
                "user_id": user_id,
                "message_length": len(str(message)),
            }
        ) as span:
            try:
                # Add session_id if available
                session_id = get_session_id()
                if session_id:
                    span.set_attribute("session_id", session_id)

                # Execute function
                result = await func(*args, **kwargs)

                # Add result attributes
                if hasattr(result, 'task_created'):
                    span.set_attribute("agent.task_created", result.task_created)
                if hasattr(result, 'needs_clarification'):
                    span.set_attribute("agent.needs_clarification", result.needs_clarification)

                return result

            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    return wrapper


def add_genai_attributes(
    span: trace.Span,
    model: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    finish_reason: Optional[str] = None
):
    """Add GenAI semantic conventions to a span.

    Args:
        span: Current span to add attributes to
        model: Model name (e.g., 'gpt-4o-mini')
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens
        total_tokens: Total tokens used
        finish_reason: Finish reason (e.g., 'stop', 'length')
    """
    span.set_attribute("gen_ai.request.model", model)
    span.set_attribute("gen_ai.system", "openai")

    if input_tokens is not None:
        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
    if output_tokens is not None:
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
    if total_tokens is not None:
        span.set_attribute("gen_ai.usage.total_tokens", total_tokens)
    if finish_reason is not None:
        span.set_attribute("gen_ai.response.finish_reason", finish_reason)
