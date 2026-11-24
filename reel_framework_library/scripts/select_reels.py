"""Pick each creator's top reels that contain speech, from the saved transcripts.

Writes data/reels_speech.csv (every reel with speech metrics) and
data/selected_reels.csv (top 10 per creator). Reels under 7 days old and reels
without speech are never selected.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import (  # noqa: E402
    REELS_PER_CREATOR_SELECTED,
    SCORED_CSV,
    SELECTED_CSV,
    SPEECH_CSV,
    TRANSCRIPTS_DIR,
)
from reel_framework_library.selection import build_speech_table, select_top, write_rows  # noqa: E402


def main() -> int:
    """Build the speech table and selection; print a summary."""
    with open(SCORED_CSV, newline="", encoding="utf-8") as handle:
        scored = list(csv.DictReader(handle))
    table = build_speech_table(scored, TRANSCRIPTS_DIR)
    selected = select_top(table, REELS_PER_CREATOR_SELECTED, TRANSCRIPTS_DIR)
    write_rows(table, SPEECH_CSV)
    write_rows(selected, SELECTED_CSV)

    eligible = [r for r in table if str(r["eligible"]) == "True"]
    speech = [r for r in eligible if r["has_speech"]]
    per_creator = Counter(r["handle"] for r in selected)
    creators = sorted({r["handle"] for r in table})
    short = {h: per_creator.get(h, 0) for h in creators if per_creator.get(h, 0) < REELS_PER_CREATOR_SELECTED}

    print(f"Reels: {len(table)} total | {len(eligible)} mature | {len(speech)} mature with speech")
    print(f"Selected {len(selected)} reels across {len(per_creator)} creators -> {SELECTED_CSV}")
    print(f"Creators with fewer than {REELS_PER_CREATOR_SELECTED} ({len(short)}):")
    for handle, n in sorted(short.items(), key=lambda kv: kv[1]):
        print(f"  {handle}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
