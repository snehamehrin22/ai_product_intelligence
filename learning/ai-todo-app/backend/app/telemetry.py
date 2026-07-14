"""OpenTelemetry instrumentation for AI Todo App.

Provides:
- Tracer configuration for LangGraph agent
- GenAI semantic conventions
- Langfuse integration for real-time trace visualization
- Zerobus trace publishing (custom exporter)
- Session ID propagation via baggage
"""

import logging
from typing import Optional, Sequence
from datetime import datetime
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

from .config import settings

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[trace.Tracer] = None

# Global Zerobus publisher (lazy-loaded)
_zerobus_publisher: Optional[object] = None


def get_zerobus_publisher():
    """Get or create Zerobus publisher for trace export.

    Returns:
        ZerobusPublisher instance (lazy-loaded)
    """
    global _zerobus_publisher
    if _zerobus_publisher is None:
        try:
            from .events import ZerobusPublisher
            _zerobus_publisher = ZerobusPublisher()
            logger.info("✓ Zerobus publisher initialized for trace export")
        except Exception as e:
            logger.error(f"Failed to initialize Zerobus publisher: {e}")
            return None
    return _zerobus_publisher


class ZerobusSpanExporter(SpanExporter):
    """Custom OTel SpanExporter that publishes traces to Zerobus (Delta Lake).

    This exporter:
    - Serializes OTel spans to JSON
    - Flattens nested attributes for easier querying
    - Extracts session_id from OTel baggage
    - Publishes to agent_traces Delta table via Zerobus
    - Handles errors gracefully (doesn't crash agent)
    """

    def __init__(self):
        """Initialize Zerobus span exporter."""
        self.publisher = get_zerobus_publisher()
        if self.publisher is None:
            logger.warning("Zerobus publisher not available - traces will not be exported to Delta Lake")

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to Zerobus (agent_traces table).

        Args:
            spans: Sequence of ReadableSpan objects from OTel SDK

        Returns:
            SpanExportResult.SUCCESS or FAILURE
        """
        if not self.publisher:
            return SpanExportResult.FAILURE

        try:
            import asyncio

            # Serialize all spans first
            trace_events = [self._serialize_span(span) for span in spans]

            # Publish all spans asynchronously
            # Note: SpanExporter runs in a background thread, so we need to handle async carefully
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If event loop is running, schedule the coroutines
                    for trace_event in trace_events:
                        asyncio.create_task(self.publisher.publish(trace_event, table="agent_traces"))
                else:
                    # If no loop is running, run synchronously
                    loop.run_until_complete(
                        asyncio.gather(*[
                            self.publisher.publish(trace_event, table="agent_traces")
                            for trace_event in trace_events
                        ])
                    )
            except RuntimeError:
                # No event loop in current thread, create a new one
                asyncio.run(
                    asyncio.gather(*[
                        self.publisher.publish(trace_event, table="agent_traces")
                        for trace_event in trace_events
                    ])
                )

            logger.debug(f"Exported {len(spans)} spans to Zerobus")
            return SpanExportResult.SUCCESS

        except Exception as e:
            logger.error(f"Failed to export spans to Zerobus: {e}")
            return SpanExportResult.FAILURE

    def _serialize_span(self, span: ReadableSpan) -> dict:
        """Serialize OTel span to Zerobus trace event format.

        Args:
            span: ReadableSpan from OTel SDK

        Returns:
            Dict with flattened trace data for Delta Lake
        """
        # Extract span context
        span_context = span.get_span_context()
        trace_id = format(span_context.trace_id, '032x')  # Convert to hex string
        span_id = format(span_context.span_id, '016x')

        # Extract parent span ID (if exists)
        parent_span_id = None
        if span.parent:
            parent_span_id = format(span.parent.span_id, '016x')

        # Extract session_id from baggage (if available)
        session_id = None
        if span.context:
            # Note: Baggage is context-local, may not be available during export
            # Session ID will be added from span attributes if present
            pass

        # Flatten span attributes
        attributes = {}
        if span.attributes:
            for key, value in span.attributes.items():
                # Convert all values to JSON-serializable types
                if isinstance(value, (str, int, float, bool)):
                    attributes[key] = value
                elif value is None:
                    attributes[key] = None
                else:
                    attributes[key] = str(value)

        # Extract session_id from span attributes (added by set_session_id)
        if 'session_id' in attributes:
            session_id = attributes['session_id']

        # Build trace event payload
        trace_event = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "span_name": span.name,
            "span_kind": span.kind.name if span.kind else "INTERNAL",
            "start_time": datetime.fromtimestamp(span.start_time / 1e9).isoformat(),  # nanoseconds to datetime
            "end_time": datetime.fromtimestamp(span.end_time / 1e9).isoformat() if span.end_time else None,
            "duration_ms": int((span.end_time - span.start_time) / 1e6) if span.end_time else None,  # nanoseconds to ms
            "status_code": span.status.status_code.name if span.status else "UNSET",
            "status_message": span.status.description if span.status and span.status.description else None,
            "attributes": attributes,
            "session_id": session_id,  # Join key for platform_events
            "timestamp": datetime.fromtimestamp(span.start_time / 1e9).isoformat()  # For partitioning/filtering
        }

        return trace_event

    def shutdown(self) -> None:
        """Shutdown the exporter (cleanup resources)."""
        logger.info("Zerobus span exporter shutdown")

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans (SDK handles batching).

        Args:
            timeout_millis: Flush timeout in milliseconds

        Returns:
            True if flush succeeded
        """
        return True


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

        # Add Zerobus span exporter (publishes to Delta Lake)
        try:
            zerobus_exporter = ZerobusSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(zerobus_exporter))
            logger.info("✓ Zerobus span exporter configured (publishes to agent_traces table)")
        except Exception as e:
            logger.warning(f"Zerobus span exporter configuration failed: {e}")

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
