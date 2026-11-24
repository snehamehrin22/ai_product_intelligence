"""Export every scored reel, with its transcript and hook/body/ending, to one CSV.

Writes data/corpus.csv (UTF-8 with BOM so Excel and Numbers open it cleanly).

Examples:
    python scripts/export_corpus.py
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import DATA_DIR, SCORED_CSV  # noqa: E402
from reel_framework_library.frameworks import has_speech, load_transcripts  # noqa: E402

OUT = DATA_DIR / "corpus.csv"
SCORE_COLS = [
    "handle", "shortcode", "url", "posted_at", "age_days", "views", "likes", "comments",
    "duration_seconds", "followers", "creator_median_views", "outlier_ratio",
    "eligible", "exclude_reason", "creator_low_sample",
]


def main() -> int:
    """Join scored reels to transcripts and write one row per reel; return an exit code."""
    transcripts = load_transcripts()
    with open(SCORED_CSV, encoding="utf-8") as fh:
        scored = list(csv.DictReader(fh))

    n_tx = n_speech = 0
    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=SCORE_COLS + [
            "has_transcript", "has_speech", "words", "hook", "body", "ending", "full_text",
        ])
        w.writeheader()
        for r in scored:
            t = transcripts.get(f"{r['handle']}/{r['shortcode']}")
            row = {c: r[c] for c in SCORE_COLS}
            row.update(has_transcript=bool(t), has_speech=False, words="", hook="", body="", ending="", full_text="")
            if t:
                n_tx += 1
                segs = [s.text.strip() for s in t.segments]
                row.update(
                    has_speech=has_speech(t),
                    words=len(t.text.split()),
                    full_text=t.text.strip(),
                    hook=segs[0] if segs else "",
                    body=" ".join(segs[1:-1]) if len(segs) > 2 else "",
                    ending=segs[-1] if len(segs) > 1 else "",
                )
                n_speech += row["has_speech"]
            w.writerow(row)
    print(f"wrote {OUT}: {len(scored)} reels, {n_tx} with transcripts, {n_speech} with speech")
    return 0


if __name__ == "__main__":
    sys.exit(main())
