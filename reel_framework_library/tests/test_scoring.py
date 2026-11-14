"""Scoring: outlier ratio, the recency rule, and low-sample flags."""

import json
from datetime import datetime, timezone

import pytest

from reel_framework_library.schemas import Reel
from reel_framework_library.scoring import age_in_days, load_followers, score_creator

AS_OF = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)


def _reel(code: str, views: int, days_old: float) -> Reel:
    posted = datetime.fromtimestamp(AS_OF.timestamp() - days_old * 86400, tz=timezone.utc)
    return Reel(shortcode=code, url=f"u/{code}", username="a", views=views, posted_at=posted.isoformat())


def test_age_in_days() -> None:
    """Age is measured from the posting time to the reference time."""
    assert age_in_days("2026-11-13T12:00:00.000Z", AS_OF) == pytest.approx(1.0)


def test_ratio_is_views_over_median_of_mature_reels() -> None:
    """Six mature reels with a median of 350; a 700-view reel scores 2.0."""
    reels = [_reel(f"m{i}", v, 20 + i) for i, v in enumerate([100, 200, 300, 400, 500, 700])]
    scored = {s.shortcode: s for s in score_creator("a", reels, AS_OF)}
    assert scored["m5"].creator_median_views == 350
    assert scored["m5"].outlier_ratio == 2.0
    assert scored["m0"].outlier_ratio == pytest.approx(0.286, abs=1e-3)


def test_young_reels_excluded_and_dont_move_the_median() -> None:
    """A 2-day-old reel with huge views must not shift anyone's score."""
    mature = [_reel(f"m{i}", 100, 20 + i) for i in range(6)]
    young = _reel("new", 1_000_000, 2)
    scored = {s.shortcode: s for s in score_creator("a", mature + [young], AS_OF)}
    assert scored["new"].eligible is False
    assert scored["new"].exclude_reason == "too_new"
    assert scored["new"].outlier_ratio is None
    assert scored["m0"].creator_median_views == 100  # unchanged by the young reel
    assert scored["m0"].outlier_ratio == 1.0


def test_boundary_exactly_seven_days_is_mature() -> None:
    """The rule is 'at least 7 days old'."""
    scored = score_creator("a", [_reel("x", 10, 7.0)] * 1, AS_OF)
    assert scored[0].eligible is True


def test_low_sample_flag() -> None:
    """Fewer than 5 mature reels flags the creator but still scores them."""
    reels = [_reel(f"m{i}", 100 * (i + 1), 20) for i in range(3)]
    scored = score_creator("a", reels, AS_OF)
    assert all(s.creator_low_sample for s in scored)
    assert all(s.outlier_ratio is not None for s in scored)


def test_creator_with_only_young_reels_has_no_ratios() -> None:
    """Nothing mature means no median and no ratios, never a crash or a divide by zero."""
    scored = score_creator("a", [_reel("n1", 50, 1), _reel("n2", 60, 3)], AS_OF)
    assert all(s.creator_median_views is None and s.outlier_ratio is None for s in scored)


def test_sorted_best_first_with_young_last() -> None:
    """Output order feeds selection: highest ratio first, ineligible at the end."""
    reels = [_reel("lo", 100, 30), _reel("hi", 900, 31), _reel("mid", 300, 32), _reel("new", 5, 1)] + [
        _reel(f"f{i}", 300, 40 + i) for i in range(4)
    ]
    order = [s.shortcode for s in score_creator("a", reels, AS_OF)]
    assert order[0] == "hi" and order[-1] == "new"


def test_load_followers(tmp_path) -> None:
    """Missing or null follower data becomes None, not an error."""
    (tmp_path / "a.json").write_text(json.dumps({"followersCount": 1234}))
    (tmp_path / "b.json").write_text(json.dumps({"followersCount": None}))
    assert load_followers(tmp_path, "a") == 1234
    assert load_followers(tmp_path, "b") is None
    assert load_followers(tmp_path, "missing") is None
