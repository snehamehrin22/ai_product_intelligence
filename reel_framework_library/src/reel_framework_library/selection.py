"""Pick each creator's top reels among those that actually contain speech."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import MIN_SPEECH_COVERAGE, MIN_WORDS, MIN_WORDS_PER_MINUTE
from .schemas import Transcript
from .transcribe import transcript_path


def speech_metrics(transcript: Optional[Transcript], reel_duration: float) -> Dict[str, Any]:
    """Measure how much of a reel is speech, from its Whisper transcript.

    Coverage is the share of the video's duration that transcript segments span,
    capped at 1 (segments can overlap slightly). words_per_minute separates real
    narration (about 160+) from sparse text or music.

    Args:
        transcript: The reel's transcript, or None if it has none.
        reel_duration: Reel length in seconds from the scraper.

    Returns:
        Dict with coverage, words, words_per_minute, language.
    """
    if transcript is None or reel_duration <= 0:
        return {"coverage": 0.0, "words": 0, "words_per_minute": 0.0, "language": None}
    spoken = sum(max(0.0, s.end - s.start) for s in transcript.segments)
    words = len(transcript.text.split())
    return {
        "coverage": round(min(1.0, spoken / reel_duration), 3),
        "words": words,
        "words_per_minute": round(words / (reel_duration / 60), 1),
        "language": transcript.language,
    }


def has_speech(metrics: Dict[str, Any]) -> bool:
    """True if a reel meets all three speech thresholds."""
    return (
        metrics["coverage"] >= MIN_SPEECH_COVERAGE
        and metrics["words"] >= MIN_WORDS
        and metrics["words_per_minute"] >= MIN_WORDS_PER_MINUTE
    )


def load_transcript(transcripts_dir: Path, handle: str, shortcode: str) -> Optional[Transcript]:
    """Load a saved transcript, or None if the reel has none."""
    path = transcript_path(transcripts_dir, handle, shortcode)
    if not path.exists():
        return None
    return Transcript(**json.loads(path.read_text(encoding="utf-8")))


def build_speech_table(scored_rows: List[Dict[str, str]], transcripts_dir: Path) -> List[Dict[str, Any]]:
    """Attach speech metrics and the has_speech verdict to every scored reel."""
    table = []
    for row in scored_rows:
        transcript = load_transcript(transcripts_dir, row["handle"], row["shortcode"])
        metrics = speech_metrics(transcript, float(row["duration_seconds"] or 0))
        table.append({**row, **metrics, "has_transcript": transcript is not None, "has_speech": has_speech(metrics)})
    return table


def select_top(table: List[Dict[str, Any]], per_creator: int, transcripts_dir: Path) -> List[Dict[str, Any]]:
    """Top reels per creator: eligible (mature), has speech, best outlier ratio first.

    Ranking is within each creator, so a viral outlier on a small account can't
    crowd out anyone else's reels.
    """
    by_creator: Dict[str, List[Dict[str, Any]]] = {}
    for row in table:
        if str(row["eligible"]) == "True" and row["has_speech"]:
            by_creator.setdefault(row["handle"], []).append(row)

    selected: List[Dict[str, Any]] = []
    for handle, rows in by_creator.items():
        rows.sort(key=lambda r: -float(r["outlier_ratio"]))
        for rank, row in enumerate(rows[:per_creator], start=1):
            selected.append({
                "handle": handle,
                "rank_in_creator": rank,
                "shortcode": row["shortcode"],
                "url": row["url"],
                "posted_at": row["posted_at"],
                "views": row["views"],
                "likes": row["likes"],
                "comments": row["comments"],
                "followers": row["followers"],
                "duration_seconds": row["duration_seconds"],
                "outlier_ratio": row["outlier_ratio"],
                "creator_median_views": row["creator_median_views"],
                "creator_low_sample": row["creator_low_sample"],
                "speech_coverage": row["coverage"],
                "words": row["words"],
                "words_per_minute": row["words_per_minute"],
                "language": row["language"],
                "transcript_path": str(transcript_path(transcripts_dir, handle, row["shortcode"])),
            })
    return selected


def write_rows(rows: List[Dict[str, Any]], path: Path) -> None:
    """Write dict rows to CSV using the first row's keys as columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
