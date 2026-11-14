"""Score each reel against its own creator's typical views."""

import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .fetch import validate_items
from .schemas import Reel, ScoredReel

# Measured on the real data (see PRD US-3): reels under ~7 days old sit at
# 55-90% of their creator's median and recover to ~100% after a week.
MIN_AGE_DAYS = 7.0

# Below this many mature reels a median is too noisy to trust; flag the creator.
MIN_MATURE_REELS = 5


def age_in_days(posted_at: str, as_of: datetime) -> float:
    """Days between posting and the scoring reference time."""
    posted = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
    return (as_of - posted).total_seconds() / 86400


def score_creator(
    handle: str,
    reels: List[Reel],
    as_of: datetime,
    followers: Optional[int] = None,
    min_age_days: float = MIN_AGE_DAYS,
    min_mature: int = MIN_MATURE_REELS,
) -> List[ScoredReel]:
    """Compute outlier ratios for one creator.

    The median uses only mature reels. Including young ones would drag the
    median down and inflate everyone else's ratio. Young reels are kept in the
    output (so nothing disappears) but marked ineligible with no ratio.

    Args:
        handle: Creator handle.
        reels: Validated reels for this creator.
        as_of: Reference time for reel age.
        followers: Follower count, for context.
        min_age_days: Reels newer than this are excluded from scoring.
        min_mature: Minimum mature reels for a reliable median.

    Returns:
        Scored reels sorted by outlier ratio, highest first (young reels last).
    """
    ages = {r.shortcode: age_in_days(r.posted_at, as_of) for r in reels}
    mature = [r for r in reels if ages[r.shortcode] >= min_age_days]
    median = statistics.median(r.views for r in mature) if mature else None
    low_sample = len(mature) < min_mature

    scored: List[ScoredReel] = []
    for reel in reels:
        is_mature = ages[reel.shortcode] >= min_age_days
        ratio = round(reel.views / median, 3) if (is_mature and median) else None
        scored.append(
            ScoredReel(
                handle=handle,
                shortcode=reel.shortcode,
                url=reel.url,
                posted_at=reel.posted_at,
                age_days=round(ages[reel.shortcode], 2),
                views=reel.views,
                likes=reel.likes,
                comments=reel.comments,
                duration_seconds=reel.duration_seconds,
                followers=followers,
                creator_median_views=median,
                outlier_ratio=ratio,
                eligible=is_mature,
                exclude_reason="" if is_mature else "too_new",
                creator_low_sample=low_sample,
            )
        )
    return sorted(scored, key=lambda s: (s.outlier_ratio is None, -(s.outlier_ratio or 0)))


def load_followers(profiles_dir: Path, handle: str) -> Optional[int]:
    """Follower count from the saved profile record, or None if missing/null."""
    path = profiles_dir / f"{handle}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("followersCount")


def score_all(
    raw_dir: Path, profiles_dir: Path, as_of: datetime, **kwargs
) -> Dict[str, List[ScoredReel]]:
    """Score every creator that has a raw file. Unparseable reels are skipped here
    (they were already written to errors.jsonl at fetch time)."""
    result: Dict[str, List[ScoredReel]] = {}
    for path in sorted(raw_dir.glob("*.json")):
        handle = path.stem
        items = json.loads(path.read_text(encoding="utf-8"))
        reels, _ = validate_items(handle, items)
        if reels:
            result[handle] = score_creator(handle, reels, as_of, load_followers(profiles_dir, handle), **kwargs)
    return result


def write_scored_csv(scored: Dict[str, List[ScoredReel]], path: Path, as_of: datetime) -> int:
    """Write all scored reels to one CSV; returns the row count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(ScoredReel.model_fields) + ["as_of"]
    rows = 0
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for reels in scored.values():
            for reel in reels:
                writer.writerow({**reel.model_dump(), "as_of": as_of.isoformat(timespec="seconds")})
                rows += 1
    return rows
