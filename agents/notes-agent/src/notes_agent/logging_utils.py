"""
Logging and observability utilities.
Every decision gets logged - this is how we understand what the agent is doing.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from .schemas import BlockClassification


def get_log_file_path() -> Path:
    """Get path to today's log file."""
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    return logs_dir / f"decisions_{today}.jsonl"


def log_decision(
    block_id: str,
    block_text: str,
    classification: Optional[BlockClassification],
    saved: bool,
    reason: str,
    error: Optional[str] = None
) -> None:
    """
    Log a classification decision.

    Args:
        block_id: Block identifier
        block_text: Block content (truncated for preview)
        classification: BlockClassification if successful, None if failed
        saved: Whether the classification was saved to Supabase
        reason: Why it was/wasn't saved
        error: Error message if classification failed
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "block_id": block_id,
        "block_text_preview": block_text[:100],
        "classification": classification.model_dump() if classification else None,
        "confidence": classification.confidence if classification else None,
        "saved": saved,
        "reason": reason,
        "error": error
    }

    log_file = get_log_file_path()

    # Append to JSONL file (one JSON object per line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def log_metrics(
    total_entries: int,
    total_blocks: int,
    blocks_saved: int,
    blocks_skipped: int,
    errors: int
) -> None:
    """
    Log processing metrics.

    Args:
        total_entries: Number of Notion entries processed
        total_blocks: Total blocks classified
        blocks_saved: Blocks saved to Supabase
        blocks_skipped: Blocks skipped (low confidence)
        errors: Number of errors encountered
    """
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "type": "metrics_summary",
        "total_entries": total_entries,
        "total_blocks": total_blocks,
        "blocks_saved": blocks_saved,
        "blocks_skipped": blocks_skipped,
        "errors": errors,
        "save_rate": f"{(blocks_saved / total_blocks * 100):.1f}%" if total_blocks > 0 else "0%"
    }

    log_file = get_log_file_path()

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics) + "\n")


def log_entry_processed(notion_entry_id: str, block_count: int, duration_seconds: float) -> None:
    """
    Log that a Notion entry was fully processed.

    Args:
        notion_entry_id: Notion page ID
        block_count: Number of blocks processed
        duration_seconds: How long processing took
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "entry_complete",
        "notion_entry_id": notion_entry_id,
        "block_count": block_count,
        "duration_seconds": round(duration_seconds, 2)
    }

    log_file = get_log_file_path()

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
