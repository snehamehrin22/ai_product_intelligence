#!/usr/bin/env python3
"""
Export Platform Event Schemas to JSON.

Generates JSON Schema documentation for all platform event types.
Output is saved to backend/docs/event_schemas.json for reference.

Usage:
    python backend/scripts/export_event_schemas.py
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.event_schemas.events import (
    PlatformEvent,
    TaskCreatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
    PageViewedEvent,
    AgentMessageSentEvent,
    AgentMessageReceivedEvent,
    SessionStartedEvent,
)


def export_schemas():
    """Export all event schemas to JSON file."""

    event_types = [
        ("PlatformEvent", PlatformEvent, "Base schema for all platform events"),
        ("TaskCreatedEvent", TaskCreatedEvent, "User creates a new task"),
        ("TaskCompletedEvent", TaskCompletedEvent, "User marks task as completed"),
        ("TaskDeletedEvent", TaskDeletedEvent, "User deletes a task"),
        ("TaskUpdatedEvent", TaskUpdatedEvent, "User updates task fields"),
        ("PageViewedEvent", PageViewedEvent, "User navigates to a page"),
        ("AgentMessageSentEvent", AgentMessageSentEvent, "User sends message to AI agent"),
        ("AgentMessageReceivedEvent", AgentMessageReceivedEvent, "AI agent responds to user"),
        ("SessionStartedEvent", SessionStartedEvent, "User session begins"),
    ]

    schemas = {}

    for name, event_class, description in event_types:
        schema = event_class.model_json_schema()
        schemas[name] = {
            "description": description,
            "schema": schema,
            "example": schema.get("examples", [{}])[0] if "examples" in schema else event_class.Config.json_schema_extra.get("example", {})
        }

    # Create docs directory if needed
    docs_dir = Path(__file__).parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    # Write to file
    output_file = docs_dir / "event_schemas.json"
    with open(output_file, "w") as f:
        json.dump(schemas, f, indent=2)

    print(f"✅ Exported {len(schemas)} event schemas to: {output_file}")
    print("\nEvent Types:")
    for name, _, description in event_types:
        print(f"  - {name}: {description}")

    # Also create markdown documentation
    create_markdown_docs(event_types, docs_dir)


def create_markdown_docs(event_types, docs_dir):
    """Create markdown documentation from schemas."""

    md_content = """# Platform Event Schemas

This document describes all platform events emitted by the AI Todo App.

## Overview

All events inherit from the base `PlatformEvent` schema and include:
- `event_id` (string): Unique identifier (UUID v4)
- `event_name` (string): Event type identifier
- `event_version` (string): Schema version (default "v1")
- `timestamp` (string): Event occurrence time (ISO8601)
- `session_id` (string): User session identifier (join key)
- `user_id` (string): User identifier
- `properties` (dict): Event-specific data

## Event Types

"""

    for name, event_class, description in event_types:
        if name == "PlatformEvent":
            continue  # Skip base class in list

        schema = event_class.model_json_schema()
        example = schema.get("examples", [{}])[0] if "examples" in schema else event_class.Config.json_schema_extra.get("example", {})

        md_content += f"### {name}\n\n"
        md_content += f"**Description:** {description}\n\n"

        # Get event_name from schema if it's a Literal type
        if hasattr(event_class, 'model_fields') and 'event_name' in event_class.model_fields:
            event_name_field = event_class.model_fields['event_name']
            event_name_default = event_name_field.default
            md_content += f"**Event Name:** `{event_name_default}`\n\n"
        else:
            md_content += f"**Event Name:** See example below\n\n"

        # Extract properties documentation from docstring
        docstring = event_class.__doc__ or ""
        if "Properties:" in docstring:
            props_section = docstring.split("Properties:")[1].split("Example:")[0].strip()
            md_content += f"**Properties:**\n{props_section}\n\n"

        md_content += f"**Example:**\n```json\n{json.dumps(example, indent=2)}\n```\n\n"
        md_content += "---\n\n"

    md_file = docs_dir / "event_schemas.md"
    with open(md_file, "w") as f:
        f.write(md_content)

    print(f"✅ Created markdown documentation: {md_file}")


if __name__ == "__main__":
    export_schemas()
