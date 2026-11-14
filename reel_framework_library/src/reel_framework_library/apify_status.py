"""Apify account checks: is the token valid, and how much can we still spend?"""

from typing import Any, Dict

import requests

from .config import APIFY_API_BASE, PROFILE_ACTOR_ID, REEL_ACTOR_ID
from .schemas import AccountStatus


class AccountCheckError(RuntimeError):
    """Raised when the Apify account can't be read or its data has an unexpected shape."""


def _event_price(actor: Dict[str, Any], event: str, tier: str) -> float:
    """Read one charge event's price for a plan tier from an actor listing.

    Tiered events (reel, profile) have a per-tier table; flat events (actor-start)
    carry a single price.
    """
    events = actor["data"]["pricingInfos"][-1]["pricingPerEvent"]["actorChargeEvents"]
    spec = events[event]
    if "eventTieredPricingUsd" in spec:
        return spec["eventTieredPricingUsd"][tier]["tieredEventPriceUsd"]
    return spec["eventPriceUsd"]


def parse_account_status(
    me: Dict[str, Any],
    limits: Dict[str, Any],
    reel_actor: Dict[str, Any],
    profile_actor: Dict[str, Any],
) -> AccountStatus:
    """Build an AccountStatus from the three Apify API responses.

    Kept separate from the HTTP calls so it can be tested with saved responses.
    The per-reel price is read for the account's own tier so estimates never use
    a hardcoded number (the price differs between Free, Starter and higher plans).

    Raises:
        AccountCheckError: If a field we rely on is missing.
    """
    try:
        user = me["data"]
        plan = user["plan"]
        tier = plan["tier"]
        cap = limits["data"]["limits"]["maxMonthlyUsageUsd"]
        spent = limits["data"]["current"]["monthlyUsageUsd"]
        price = _event_price(reel_actor, "reel", tier)
        profile_price = _event_price(profile_actor, "profile", tier)
        start_fee = _event_price(reel_actor, "actor-start", tier)
    except (KeyError, IndexError, TypeError) as exc:
        raise AccountCheckError(f"unexpected Apify response shape: missing {exc!r}") from exc

    return AccountStatus(
        username=user["username"],
        plan=plan["id"],
        tier=tier,
        monthly_cap_usd=cap,
        spent_usd=spent,
        price_per_reel_usd=price,
        price_per_profile_usd=profile_price,
        start_fee_usd=start_fee,
    )


def _get_json(url: str, token: str) -> Dict[str, Any]:
    """GET a JSON document from Apify with bearer auth."""
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if response.status_code != 200:
        # Status only: the body can echo request details, and we never log the token.
        raise AccountCheckError(f"Apify returned HTTP {response.status_code} for {url}")
    return response.json()


def fetch_account_status(token: str) -> AccountStatus:
    """Call Apify and return the current account status.

    Raises:
        AccountCheckError: If the token is rejected or any call fails.
    """
    me = _get_json(f"{APIFY_API_BASE}/users/me", token)
    limits = _get_json(f"{APIFY_API_BASE}/users/me/limits", token)
    reel_actor = _get_json(f"{APIFY_API_BASE}/acts/{REEL_ACTOR_ID}", token)
    profile_actor = _get_json(f"{APIFY_API_BASE}/acts/{PROFILE_ACTOR_ID}", token)
    return parse_account_status(me, limits, reel_actor, profile_actor)
