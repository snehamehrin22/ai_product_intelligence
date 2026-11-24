"""Split every speech reel into hook / body / ending with plain code (no LLM).

Hook = first Whisper segment, ending = last segment, body = everything between.
Writes data/frameworks/hbe.jsonl.

Examples:
    python scripts/split_reels.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import FRAMEWORKS_DIR  # noqa: E402
from reel_framework_library.frameworks import has_speech, load_transcripts, outlier_ratios  # noqa: E402


def main() -> int:
    """Write one JSON line per speech reel; return an exit code."""
    transcripts, ratios = load_transcripts(), outlier_ratios()
    FRAMEWORKS_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(FRAMEWORKS_DIR / "hbe.jsonl", "w", encoding="utf-8") as fh:
        for rid, t in transcripts.items():
            if rid not in ratios or not has_speech(t) or len(t.segments) < 3:
                continue
            segs = [s.text.strip() for s in t.segments]
            rec = {
                "id": rid,
                "handle": t.handle,
                "outlier": ratios[rid],
                "seconds": round(t.audio_duration_seconds or 0),
                "hook": segs[0],
                "body": " ".join(segs[1:-1]),
                "ending": segs[-1],
            }
            fh.write(json.dumps(rec) + "\n")
            n += 1
    print(f"split {n} reels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
