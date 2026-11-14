"""Transcribe every scored reel with Whisper. Transcripts only, no analysis.

Prints an estimate first and stops if it exceeds --max-usd. Resumable.

Examples:
    python scripts/transcribe_reels.py --dry-run
    python scripts/transcribe_reels.py --limit 1          # try one reel
    python scripts/transcribe_reels.py
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import (  # noqa: E402
    ERRORS_JSONL,
    PROJECT_ROOT,
    RAW_DIR,
    SCORED_CSV,
    TRANSCRIBE_WORKERS,
    TRANSCRIPTION_MODEL,
    TRANSCRIPTS_DIR,
    WHISPER_USD_PER_MINUTE,
)
from reel_framework_library.openai_status import check_openai  # noqa: E402
from reel_framework_library.transcribe import (  # noqa: E402
    estimate_cost,
    load_audio_urls,
    pending,
    queue_from_scored,
    transcribe_all,
)


def main() -> int:
    """Run the transcription; return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, help="only the first N pending reels (best first)")
    parser.add_argument("--max-usd", type=float, default=10.0, help="refuse to start above this estimate")
    parser.add_argument("--workers", type=int, default=TRANSCRIBE_WORKERS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("FAIL: OPENAI_API_KEY is not set")
        return 1
    try:
        print(f"OpenAI: {check_openai(key)}")
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        return 1

    todo = pending(queue_from_scored(SCORED_CSV), TRANSCRIPTS_DIR)
    if args.limit:
        todo = todo[: args.limit]
    minutes, usd = estimate_cost(todo, WHISPER_USD_PER_MINUTE)
    print(f"{len(todo)} reels to transcribe, {minutes} min of audio, estimated ${usd:.2f} at ${WHISPER_USD_PER_MINUTE}/min (price not verified)")
    if not todo:
        return 0
    if usd > args.max_usd:
        print(f"FAIL: estimate is over --max-usd {args.max_usd}")
        return 1
    if args.dry_run:
        return 0

    result = transcribe_all(
        OpenAI(api_key=key, max_retries=5), TRANSCRIPTION_MODEL, todo, load_audio_urls(RAW_DIR),
        TRANSCRIPTS_DIR, ERRORS_JSONL, workers=args.workers,
    )
    print(f"\nDone: {result['done']}  failed: {len(result['failed'])}  no audio url: {result['skipped_no_audio']}")
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
