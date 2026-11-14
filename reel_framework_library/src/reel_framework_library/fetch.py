"""Fetch reels from Apify and save raw results per creator.

The Apify client is passed in, so tests can supply a fake and never spend money.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pydantic import ValidationError

from .schemas import AccountStatus, Reel


def chunk(items: List[str], size: int) -> List[List[str]]:
    """Split a list into consecutive batches of at most `size`."""
    return [items[i : i + size] for i in range(0, len(items), size)]


def estimate_cost(
    n_creators: int, reels_per_creator: int, batch_size: int, status: AccountStatus
) -> float:
    """Worst-case spend: every creator returns the full reel count.

    Includes the flat start fee per reel run, plus one profile run (for follower
    counts). Real spend is usually a little lower because some creators have
    fewer reels than the limit.
    """
    if n_creators == 0:
        return 0.0
    reel_runs = -(-n_creators // batch_size)  # ceiling division
    reels = n_creators * reels_per_creator * status.price_per_reel_usd
    profiles = n_creators * status.price_per_profile_usd
    return round(reels + profiles + (reel_runs + 1) * status.start_fee_usd, 4)


def build_reel_run_input(handles: List[str], reels_per_creator: int) -> Dict[str, Any]:
    """Input for the reel scraper.

    Pinned reels are skipped because they are often old, so they break the
    'most recent N reels' window the outlier ratio is computed over. Trial reels
    are shown to non-followers first and have unrepresentative numbers.
    """
    return {
        "username": handles,
        "resultsLimit": reels_per_creator,
        "skipPinnedPosts": True,
        "skipTrialReels": True,
    }


def parse_reel(item: Dict[str, Any]) -> Reel:
    """Convert one raw scraper item into a validated Reel.

    Raises:
        pydantic.ValidationError: If views (videoPlayCount) or another required
            field is missing.
    """
    return Reel(
        shortcode=item.get("shortCode") or "",
        url=item.get("url") or "",
        username=(item.get("ownerUsername") or "").lower(),
        views=item.get("videoPlayCount"),
        likes=item.get("likesCount"),
        comments=item.get("commentsCount"),
        duration_seconds=item.get("videoDuration"),
        posted_at=item.get("timestamp") or "",
        caption=item.get("caption") or "",
        audio_url=item.get("audioUrl"),
        video_url=item.get("videoUrl"),
        product_type=item.get("productType"),
    )


def group_by_creator(items: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group raw items by the (lowercased) account that owns them."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        owner = (item.get("ownerUsername") or "").lower()
        grouped.setdefault(owner, []).append(item)
    return grouped


def validate_items(
    handle: str, items: List[Dict[str, Any]]
) -> Tuple[List[Reel], List[Dict[str, Any]]]:
    """Parse a creator's raw items; collect failures instead of dropping them.

    Returns:
        (valid reels, error records ready for errors.jsonl).
    """
    reels: List[Reel] = []
    errors: List[Dict[str, Any]] = []
    for item in items:
        try:
            reels.append(parse_reel(item))
        except ValidationError as exc:
            errors.append(
                {
                    "handle": handle,
                    "shortcode": item.get("shortCode"),
                    "stage": "parse_reel",
                    "error": "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors()),
                }
            )
    return reels, errors


def raw_path(raw_dir: Path, handle: str) -> Path:
    """Where a creator's raw scraper output lives."""
    return raw_dir / f"{handle}.json"


def save_raw(raw_dir: Path, handle: str, items: List[Dict[str, Any]]) -> None:
    """Write raw items to disk untouched. Apify deletes datasets after 7 days."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path(raw_dir, handle).write_text(json.dumps(items, indent=1, default=str), encoding="utf-8")


def append_errors(errors_path: Path, records: List[Dict[str, Any]]) -> None:
    """Append error records, one JSON object per line, each stamped with a time."""
    if not records:
        return
    errors_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(errors_path, "a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps({"ts": stamp, **record}) + "\n")


def pending_handles(handles: List[str], raw_dir: Path) -> List[str]:
    """Creators with no saved raw file yet, so a re-run resumes where it stopped."""
    return [h for h in handles if not raw_path(raw_dir, h).exists()]


def fetch_reels(
    client: Any,
    handles: List[str],
    reels_per_creator: int,
    batch_size: int,
    raw_dir: Path,
    errors_path: Path,
    actor_id: str,
) -> Dict[str, Any]:
    """Scrape reels for creators in batches and save each creator's raw JSON.

    A creator is saved the moment its batch finishes. A creator that returns no
    reels, or whose reels all lack views, is recorded in errors.jsonl and loudly
    reported; the all-null-views case is the bug the first analyzer shipped with.

    Args:
        client: An ApifyClient (or a test fake with the same two calls).
        handles: Creators to fetch (already filtered to the pending ones).
        reels_per_creator: Max reels per creator.
        batch_size: Creators per scraper run.
        raw_dir: Directory for data/raw/{handle}.json.
        errors_path: errors.jsonl path.
        actor_id: Apify reel scraper actor id.

    Returns:
        Summary dict: saved, failed, spent_usd.
    """
    saved: List[str] = []
    failed: List[str] = []
    spent = 0.0

    for number, batch in enumerate(chunk(handles, batch_size), start=1):
        print(f"[batch {number}] scraping {len(batch)} creators: {', '.join(batch)}")
        run = client.actor(actor_id).call(run_input=build_reel_run_input(batch, reels_per_creator))
        spent += float(getattr(run, "usage_total_usd", None) or 0.0)
        items = list(client.dataset(run.default_dataset_id).iterate_items())
        grouped = group_by_creator(items)

        for handle in batch:
            creator_items = grouped.get(handle, [])
            if not creator_items:
                append_errors(errors_path, [{"handle": handle, "stage": "fetch", "error": "no reels returned"}])
                failed.append(handle)
                print(f"  FAIL {handle}: no reels returned")
                continue

            # Save first, validate second: raw data must survive any parsing problem.
            save_raw(raw_dir, handle, creator_items)
            reels, errors = validate_items(handle, creator_items)
            append_errors(errors_path, errors)

            if not reels:
                failed.append(handle)
                print(f"  FAIL {handle}: {len(creator_items)} reels, none have views")
            else:
                saved.append(handle)
                note = f" ({len(errors)} without views)" if errors else ""
                print(f"  ok   {handle}: {len(reels)} reels{note}")

    return {"saved": saved, "failed": failed, "spent_usd": round(spent, 4)}


def fetch_profiles(
    client: Any, handles: List[str], profiles_dir: Path, errors_path: Path, actor_id: str
) -> Dict[str, Any]:
    """Fetch follower counts and save a small profile record per creator.

    The profile scraper returns no views, so this is only context (account size).
    """
    profiles_dir.mkdir(parents=True, exist_ok=True)
    todo = [h for h in handles if not (profiles_dir / f"{h}.json").exists()]
    if not todo:
        return {"saved": [], "failed": [], "spent_usd": 0.0}

    run = client.actor(actor_id).call(run_input={"usernames": todo})
    spent = float(getattr(run, "usage_total_usd", None) or 0.0)
    by_name = {
        (item.get("username") or "").lower(): item
        for item in client.dataset(run.default_dataset_id).iterate_items()
    }

    saved, failed = [], []
    for handle in todo:
        item = by_name.get(handle)
        if not item:
            append_errors(errors_path, [{"handle": handle, "stage": "profile", "error": "no profile returned"}])
            failed.append(handle)
            continue
        record = {
            key: item.get(key)
            for key in ("username", "fullName", "followersCount", "followsCount", "postsCount", "verified", "private", "biography")
        }
        (profiles_dir / f"{handle}.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
        saved.append(handle)
    return {"saved": saved, "failed": failed, "spent_usd": round(spent, 4)}
