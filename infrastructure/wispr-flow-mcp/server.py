#!/usr/bin/env python3
"""
Wispr Flow MCP Server
Exposes local Wispr Flow dictation history to Claude via MCP.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence
import asyncio

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio


# Wispr Flow database path
DB_PATH = Path.home() / "Library" / "Application Support" / "Wispr Flow" / "flow.sqlite"


def get_db_connection():
    """Get read-only connection to Wispr Flow database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Wispr Flow database not found at {DB_PATH}")

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def format_dictation(row: sqlite3.Row) -> dict[str, Any]:
    """Format a database row into a clean dictation object."""
    return {
        "id": row["transcriptEntityId"],
        "timestamp": row["timestamp"],
        "app": row["app"] or "Unknown",
        "text": row["formattedText"] or row["asrText"] or "",
        "word_count": row["numWords"] or 0,
        "duration_seconds": row["duration"] or 0,
        "language": row["language"] or row["detectedLanguage"],
    }


async def search_dictations(
    query: str = "",
    app: str = "",
    limit: int = 20,
    start_date: str = "",
    end_date: str = ""
) -> list[dict[str, Any]]:
    """Search dictations by text content, app, and date range."""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        SELECT transcriptEntityId, timestamp, app, formattedText, asrText,
               numWords, duration, language, detectedLanguage
        FROM History
        WHERE isArchived = 0
    """
    params = []

    if query:
        sql += " AND (formattedText LIKE ? OR asrText LIKE ?)"
        search_term = f"%{query}%"
        params.extend([search_term, search_term])

    if app:
        sql += " AND app LIKE ?"
        params.append(f"%{app}%")

    if start_date:
        sql += " AND timestamp >= ?"
        params.append(start_date)

    if end_date:
        sql += " AND timestamp <= ?"
        params.append(end_date)

    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(sql, params)
    results = [format_dictation(row) for row in cursor.fetchall()]
    conn.close()

    return results


async def get_recent_dictations(limit: int = 10) -> list[dict[str, Any]]:
    """Get most recent dictations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transcriptEntityId, timestamp, app, formattedText, asrText,
               numWords, duration, language, detectedLanguage
        FROM History
        WHERE isArchived = 0
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    results = [format_dictation(row) for row in cursor.fetchall()]
    conn.close()

    return results


async def get_dictation_by_id(transcript_id: str) -> dict[str, Any] | None:
    """Get full details for a specific dictation by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transcriptEntityId, timestamp, app, url, formattedText, asrText,
               editedText, numWords, duration, language, detectedLanguage,
               textboxContents, status, e2eLatency
        FROM History
        WHERE transcriptEntityId = ?
    """, (transcript_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["transcriptEntityId"],
        "timestamp": row["timestamp"],
        "app": row["app"] or "Unknown",
        "url": row["url"],
        "formatted_text": row["formattedText"] or "",
        "raw_transcription": row["asrText"] or "",
        "edited_text": row["editedText"],
        "word_count": row["numWords"] or 0,
        "duration_seconds": row["duration"] or 0,
        "language": row["language"] or row["detectedLanguage"],
        "textbox_context": row["textboxContents"],
        "status": row["status"],
        "latency_ms": row["e2eLatency"],
    }


async def get_dictation_stats(days: int = 7) -> dict[str, Any]:
    """Get usage statistics for recent dictations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total counts
    cursor.execute("SELECT COUNT(*) as total FROM History WHERE isArchived = 0")
    total = cursor.fetchone()["total"]

    # Recent activity (last N days)
    cursor.execute("""
        SELECT COUNT(*) as recent_count,
               SUM(numWords) as total_words,
               SUM(duration) as total_duration
        FROM History
        WHERE isArchived = 0
          AND timestamp >= datetime('now', ?)
    """, (f"-{days} days",))

    recent = cursor.fetchone()

    # Top apps
    cursor.execute("""
        SELECT app, COUNT(*) as count
        FROM History
        WHERE isArchived = 0
          AND timestamp >= datetime('now', ?)
        GROUP BY app
        ORDER BY count DESC
        LIMIT 5
    """, (f"-{days} days",))

    top_apps = [{"app": row["app"] or "Unknown", "count": row["count"]}
                for row in cursor.fetchall()]

    conn.close()

    return {
        "total_dictations": total,
        f"last_{days}_days": {
            "dictation_count": recent["recent_count"] or 0,
            "total_words": recent["total_words"] or 0,
            "total_duration_seconds": recent["total_duration"] or 0,
            "top_apps": top_apps,
        }
    }


# Initialize MCP server
app = Server("wispr-flow-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_dictations",
            description="Search Wispr Flow dictation history by text content, app, or date range. Returns formatted text from matching dictations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for in dictations (searches both formatted and raw text)",
                    },
                    "app": {
                        "type": "string",
                        "description": "Filter by application name (e.g., 'Chrome', 'Slack', 'Code')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date filter (ISO format: YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date filter (ISO format: YYYY-MM-DD)",
                    },
                },
            },
        ),
        Tool(
            name="get_recent_dictations",
            description="Get the most recent dictations from Wispr Flow history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent dictations to retrieve (default: 10)",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="get_dictation_by_id",
            description="Retrieve full details for a specific dictation by its transcript ID. Returns formatted text, raw transcription, context, and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript_id": {
                        "type": "string",
                        "description": "The transcriptEntityId (UUID) of the dictation to retrieve",
                    },
                },
                "required": ["transcript_id"],
            },
        ),
        Tool(
            name="get_dictation_stats",
            description="Get usage statistics for Wispr Flow dictations (word count, frequency, top apps).",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to include in recent activity stats (default: 7)",
                        "default": 7,
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    try:
        if name == "search_dictations":
            results = await search_dictations(
                query=arguments.get("query", ""),
                app=arguments.get("app", ""),
                limit=arguments.get("limit", 20),
                start_date=arguments.get("start_date", ""),
                end_date=arguments.get("end_date", ""),
            )
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_recent_dictations":
            results = await get_recent_dictations(limit=arguments.get("limit", 10))
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_dictation_by_id":
            result = await get_dictation_by_id(arguments["transcript_id"])
            if result is None:
                return [TextContent(type="text", text=json.dumps({"error": "Dictation not found"}))]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_dictation_stats":
            stats = await get_dictation_stats(days=arguments.get("days", 7))
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]

        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
