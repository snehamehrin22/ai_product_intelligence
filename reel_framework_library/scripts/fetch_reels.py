"""Fetch reels (and follower counts) for the creators in data/creators.csv.

Prints a cost estimate first and refuses to run if it would eat into the
reserved budget. Resumable: creators already saved in data/raw/ are skipped.

Examples:
    python scripts/fetch_reels.py --dry-run
    python scripts/fetch_reels.py --handles thoughtfully_designed,eyes_of_apoorva
    python scripts/fetch_reels.py
"""

import argparse
import os
import sys
from pathlib import Path

from apify_client import ApifyClient
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.apify_status import AccountCheckError, fetch_account_status  # noqa: E402
from reel_framework_library.config import (  # noqa: E402
    BATCH_SIZE,
    CREATORS_CSV,
    ERRORS_JSONL,
    MIN_REMAINING_BUDGET_USD,
    PROFILE_ACTOR_ID,
    PROFILES_DIR,
    PROJECT_ROOT,
    RAW_DIR,
    REEL_ACTOR_ID,
    REELS_PER_CREATOR,
)
from reel_framework_library.creators import load_creators  # noqa: E402
from reel_framework_library.fetch import (  # noqa: E402
    estimate_cost,
    fetch_profiles,
    fetch_reels,
    pending_handles,
)


def main() -> int:
    """Run the fetch; return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--handles", help="comma-separated subset of creators (default: all in creators.csv)")
    parser.add_argument("--reels", type=int, default=REELS_PER_CREATOR, help="reels per creator")
    parser.add_argument("--dry-run", action="store_true", help="show the estimate and stop")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    token = os.environ.get("APIFY_API_KEY")
    if not token:
        print("FAIL: APIFY_API_KEY is not set")
        return 1
    try:
        status = fetch_account_status(token)
    except AccountCheckError as exc:
        print(f"FAIL: {exc}")
        return 1

    all_handles = [c.handle for c in load_creators(CREATORS_CSV).creators]
    wanted = [h.strip().lower() for h in args.handles.split(",")] if args.handles else all_handles
    unknown = [h for h in wanted if h not in all_handles]
    if unknown:
        print(f"FAIL: not in creators.csv: {', '.join(unknown)}")
        return 1

    todo = pending_handles(wanted, RAW_DIR)
    estimate = estimate_cost(len(todo), args.reels, BATCH_SIZE, status)
    print(f"Creators: {len(wanted)} requested, {len(wanted) - len(todo)} already saved, {len(todo)} to fetch")
    print(f"Estimated worst-case cost: ${estimate:.2f}  (remaining ${status.remaining_usd:.2f})")

    if not todo:
        print("Nothing to fetch.")
        return 0
    if estimate > status.remaining_usd - MIN_REMAINING_BUDGET_USD:
        print(f"FAIL: estimate would leave less than ${MIN_REMAINING_BUDGET_USD:.2f} of budget")
        return 1
    if args.dry_run:
        return 0

    client = ApifyClient(token)
    reels = fetch_reels(client, todo, args.reels, BATCH_SIZE, RAW_DIR, ERRORS_JSONL, REEL_ACTOR_ID)
    profiles = fetch_profiles(client, wanted, PROFILES_DIR, ERRORS_JSONL, PROFILE_ACTOR_ID)

    spent = reels["spent_usd"] + profiles["spent_usd"]
    print(f"\nReels:    {len(reels['saved'])} creators saved, {len(reels['failed'])} failed")
    print(f"Profiles: {len(profiles['saved'])} saved, {len(profiles['failed'])} failed")
    print(f"Spent this run: ${spent:.4f} (estimate was ${estimate:.2f})")
    if reels["failed"]:
        print(f"Failed creators (see {ERRORS_JSONL.name}): {', '.join(reels['failed'])}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
