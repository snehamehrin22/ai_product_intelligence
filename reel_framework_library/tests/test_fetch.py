"""Reel fetching, using a fake Apify client so no test ever spends money."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from reel_framework_library.fetch import (
    build_reel_run_input,
    chunk,
    estimate_cost,
    fetch_profiles,
    fetch_reels,
    group_by_creator,
    parse_reel,
    pending_handles,
    validate_items,
)
from reel_framework_library.schemas import AccountStatus

INPUTS = Path(__file__).parent / "inputs"
SAMPLE = json.loads((INPUTS / "reel_items_sample.json").read_text())


class FakeClient:
    """Stands in for ApifyClient: returns canned items and counts runs."""

    def __init__(self, items):
        self.items = items
        self.runs = []

    def actor(self, actor_id):
        return SimpleNamespace(call=lambda run_input: self._call(run_input))

    def _call(self, run_input):
        self.runs.append(run_input)
        return SimpleNamespace(default_dataset_id="ds", usage_total_usd=0.01)

    def dataset(self, dataset_id):
        return SimpleNamespace(iterate_items=lambda: iter(self.items))


def _status() -> AccountStatus:
    return AccountStatus(
        username="u", plan="STARTER", tier="BRONZE", monthly_cap_usd=19, spent_usd=0,
        price_per_reel_usd=0.0023, price_per_profile_usd=0.0023, start_fee_usd=0.001,
    )


def test_parse_reel_reads_play_count_not_view_count() -> None:
    """The bug from the first analyzer: videoViewCount is None, videoPlayCount has the views."""
    item = SAMPLE[0]
    assert item["videoViewCount"] is None
    reel = parse_reel(item)
    assert reel.views == item["videoPlayCount"] > 0
    assert reel.username == "eyes_of_apoorva"


def test_null_views_fails_validation() -> None:
    """A reel with no views is an error record, not a blank row."""
    broken = copy.deepcopy(SAMPLE[0])
    broken["videoPlayCount"] = None
    reels, errors = validate_items("eyes_of_apoorva", [SAMPLE[1], broken])
    assert len(reels) == 1
    assert errors[0]["stage"] == "parse_reel" and "views" in errors[0]["error"]


def test_chunk_and_estimate() -> None:
    """52 creators in batches of 10 is 6 reel runs, plus 1 profile run."""
    assert [len(b) for b in chunk([str(i) for i in range(52)], 10)] == [10] * 5 + [2]
    cost = estimate_cost(52, 30, 10, _status())
    assert cost == pytest.approx(52 * 30 * 0.0023 + 52 * 0.0023 + 7 * 0.001, abs=1e-4)
    assert estimate_cost(0, 30, 10, _status()) == 0.0


def test_run_input_skips_pinned_and_trial() -> None:
    """Window must be the N most recent reels, with no pinned or trial reels."""
    run_input = build_reel_run_input(["a", "b"], 30)
    assert run_input["resultsLimit"] == 30
    assert run_input["skipPinnedPosts"] and run_input["skipTrialReels"]


def test_group_by_creator_lowercases() -> None:
    """Owner names are matched case-insensitively."""
    grouped = group_by_creator([{"ownerUsername": "Alpha"}, {"ownerUsername": "alpha"}, {"ownerUsername": "beta"}])
    assert {k: len(v) for k, v in grouped.items()} == {"alpha": 2, "beta": 1}


def test_fetch_saves_raw_per_creator_and_reports_missing(tmp_path) -> None:
    """Saved creators get a raw file; a creator with no reels is an error, not silence."""
    client = FakeClient(SAMPLE)
    result = fetch_reels(
        client, ["eyes_of_apoorva", "thoughtfully_designed", "ghost_account"], 30, 10,
        tmp_path / "raw", tmp_path / "errors.jsonl", "actor",
    )
    assert sorted(result["saved"]) == ["eyes_of_apoorva", "thoughtfully_designed"]
    assert result["failed"] == ["ghost_account"]
    assert len(json.loads((tmp_path / "raw" / "eyes_of_apoorva.json").read_text())) == 2
    assert not (tmp_path / "raw" / "ghost_account.json").exists()
    errors = [json.loads(l) for l in (tmp_path / "errors.jsonl").read_text().splitlines()]
    assert errors[0]["handle"] == "ghost_account" and "ts" in errors[0]
    assert len(client.runs) == 1  # three creators, one batch, one start fee


def test_all_null_views_creator_is_failed_but_raw_is_kept(tmp_path) -> None:
    """The exact first-analyzer bug: every reel lacks views. Must fail loudly, raw preserved."""
    items = copy.deepcopy(SAMPLE[:2])
    for item in items:
        item["videoPlayCount"] = None
    result = fetch_reels(FakeClient(items), ["eyes_of_apoorva"], 30, 10, tmp_path / "raw", tmp_path / "e.jsonl", "a")
    assert result["failed"] == ["eyes_of_apoorva"] and result["saved"] == []
    assert (tmp_path / "raw" / "eyes_of_apoorva.json").exists()
    assert len((tmp_path / "e.jsonl").read_text().splitlines()) == 2


def test_rerun_skips_creators_already_saved(tmp_path) -> None:
    """Resume: a creator with a raw file is not fetched (or paid for) again."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "eyes_of_apoorva.json").write_text("[]")
    assert pending_handles(["eyes_of_apoorva", "thoughtfully_designed"], raw) == ["thoughtfully_designed"]


def test_fetch_profiles_saves_followers_and_skips_existing(tmp_path) -> None:
    """Profile records keep only the small context fields."""
    client = FakeClient([{"username": "Alpha", "followersCount": 1234, "latestPosts": ["big"], "fullName": "A"}])
    result = fetch_profiles(client, ["alpha", "beta"], tmp_path / "p", tmp_path / "e.jsonl", "actor")
    assert result["saved"] == ["alpha"] and result["failed"] == ["beta"]
    saved = json.loads((tmp_path / "p" / "alpha.json").read_text())
    assert saved["followersCount"] == 1234 and "latestPosts" not in saved
    again = fetch_profiles(FakeClient([]), ["alpha"], tmp_path / "p", tmp_path / "e.jsonl", "actor")
    assert again["saved"] == [] and again["failed"] == []
