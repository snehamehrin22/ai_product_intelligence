"""Score every fetched reel against its creator's median views.

Writes data/reels_scored.csv. Reels younger than 7 days are kept but marked
ineligible, because they are still gaining views.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import DATA_DIR, PROFILES_DIR, RAW_DIR  # noqa: E402
from reel_framework_library.scoring import MIN_AGE_DAYS, score_all, write_scored_csv  # noqa: E402


def main() -> int:
    """Score reels, write the CSV, run sanity checks; return an exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", help="reference time, ISO format (default: now, UTC)")
    args = parser.parse_args()
    as_of = datetime.fromisoformat(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    scored = score_all(RAW_DIR, PROFILES_DIR, as_of)
    if not scored:
        print("FAIL: no raw data in data/raw/")
        return 1
    out = DATA_DIR / "reels_scored.csv"
    rows = write_scored_csv(scored, out, as_of)

    all_reels = [r for reels in scored.values() for r in reels]
    eligible = [r for r in all_reels if r.eligible]
    no_mature = [h for h, reels in scored.items() if not any(r.eligible for r in reels)]
    low = sorted(h for h, reels in scored.items() if reels[0].creator_low_sample)
    print(f"Scored {rows} reels from {len(scored)} creators -> {out}")
    print(f"Eligible: {len(eligible)}  |  too new (<{MIN_AGE_DAYS:g} days): {rows - len(eligible)}")
    print(f"Creators with a low-sample median (<5 mature reels): {', '.join(low) or 'none'}")
    if no_mature:
        print(f"FAIL: creators with no mature reels: {', '.join(no_mature)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
