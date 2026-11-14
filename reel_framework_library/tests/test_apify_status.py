"""Apify account parsing, using saved responses so tests never hit the network."""

import copy
import json
from pathlib import Path

import pytest

from reel_framework_library.apify_status import AccountCheckError, parse_account_status

INPUTS = Path(__file__).parent / "inputs"


def _load(name: str) -> dict:
    return json.loads((INPUTS / name).read_text())


def test_parse_uses_the_accounts_own_tier_price() -> None:
    """BRONZE account pays the BRONZE price, not the FREE one."""
    status = parse_account_status(_load("apify_me.json"), _load("apify_limits.json"), _load("apify_actor.json"))
    assert status.price_per_reel_usd == 0.0023
    assert status.monthly_cap_usd == 19
    assert status.remaining_usd == 14.5


def test_free_tier_gets_free_price() -> None:
    """Same actor listing, different tier, different price."""
    me = _load("apify_me.json")
    me["data"]["plan"]["tier"] = "FREE"
    status = parse_account_status(me, _load("apify_limits.json"), _load("apify_actor.json"))
    assert status.price_per_reel_usd == 0.0026


def test_missing_field_raises_clear_error() -> None:
    """If Apify changes its response shape we want a loud, specific failure."""
    limits = copy.deepcopy(_load("apify_limits.json"))
    del limits["data"]["current"]
    with pytest.raises(AccountCheckError, match="unexpected Apify response shape"):
        parse_account_status(_load("apify_me.json"), limits, _load("apify_actor.json"))


def test_unknown_tier_raises() -> None:
    """A tier with no listed price must not fall back to a guess."""
    me = _load("apify_me.json")
    me["data"]["plan"]["tier"] = "MYSTERY"
    with pytest.raises(AccountCheckError):
        parse_account_status(me, _load("apify_limits.json"), _load("apify_actor.json"))
