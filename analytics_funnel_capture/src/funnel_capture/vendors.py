"""Classify requests by analytics vendor and parse event names/properties.

Pure functions, no I/O. Rules are ordered; first match wins.
"""
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

# (vendor, host regex, path regex). Path regex None means any path.
VENDOR_RULES: List[Tuple[str, str, Optional[str]]] = [
    ("ga4", r"(^|\.)(google-analytics|analytics\.google)\.com$", r"/g/collect"),
    ("google_ads", r"(^|\.)(doubleclick\.net|google\.com|google\.[a-z.]+)$", r"/(pagead|ccm/collect|rmkt)"),
    ("meta_pixel", r"(^|\.)facebook\.(com|net)$", r"^/tr"),
    ("tiktok_pixel", r"(^|\.)tiktok\.com$", r"/(api/v\d/pixel|i18n/pixel)"),
    ("linkedin", r"(^|\.)ads\.linkedin\.com$", None),
    ("clarity", r"(^|\.)clarity\.ms$", r"/collect"),
    ("segment", r"(^|\.)segment\.(io|com)$", r"/v1/"),
    ("amplitude", r"(^|\.)amplitude\.com$", None),
    ("mixpanel", r"(^|\.)mixpanel\.com$", r"/(track|engage|decide)"),
    ("posthog", r"(^|\.)posthog\.com$", r"/(e|i/v0/e|batch|decide|flags)"),
    ("klaviyo", r"(^|\.)klaviyo\.com$", r"/(client|api)/"),
    ("hotjar", r"(^|\.)hotjar\.(com|io)$", None),
    ("pinterest", r"(^|\.)pinterest\.com$", r"/(ct|v3)"),
    ("snap_pixel", r"(^|\.)snapchat\.com$", None),
    ("statsig", r"(^|\.)statsig(api)?\.com$", None),
    ("launchdarkly", r"(^|\.)launchdarkly\.com$", None),
]

_COMPILED = [
    (v, re.compile(h), re.compile(p) if p else None) for v, h, p in VENDOR_RULES
]


def classify(url: str) -> Optional[str]:
    """Return the vendor label for a URL, or None if it isn't analytics.

    Args:
        url: Full request URL.
    """
    parsed = urlparse(url)
    for vendor, host_re, path_re in _COMPILED:
        if host_re.search(parsed.hostname or "") and (
            path_re is None or path_re.search(parsed.path)
        ):
            return vendor
    return None


def _flatten(qs: Dict[str, List[str]]) -> Dict[str, Any]:
    return {k: v[0] if len(v) == 1 else v for k, v in qs.items()}


def parse_ga4(url: str, body: Optional[str]) -> Tuple[List[str], Dict[str, Any]]:
    """Parse GA4 /g/collect into event names and properties.

    GA4 sends the first event in the query string and, when batching, one
    event per line in the POST body. Params prefixed ep. / epn. are custom
    event params (string / number); up. are user properties.
    """
    base = _flatten(parse_qs(urlparse(url).query))
    lines = [base] + [_flatten(parse_qs(l)) for l in (body or "").splitlines() if l.strip()]
    names: List[str] = []
    props: Dict[str, Any] = {"tid": base.get("tid"), "dl": base.get("dl"), "dt": base.get("dt")}
    for i, line in enumerate(lines):
        en = line.get("en")
        if not en:
            continue
        names.append(en)
        for k, v in line.items():
            if k.startswith(("ep.", "epn.", "up.", "upn.")) or k in ("cu", "pr1", "pr2", "pr3"):
                props[f"{en}#{i}.{k}"] = v
    return names, {k: v for k, v in props.items() if v is not None}


def parse_meta(url: str) -> Tuple[List[str], Dict[str, Any]]:
    """Parse Meta pixel /tr request: ev= is the event name, cd[...] are custom data."""
    qs = _flatten(parse_qs(urlparse(url).query))
    name = qs.get("ev")
    props = {k: v for k, v in qs.items() if k.startswith("cd[") or k in ("dl", "id")}
    return ([name] if name else []), props


def parse_json_events(body: Optional[str]) -> Tuple[List[str], Dict[str, Any]]:
    """Best-effort event-name extraction from JSON bodies (Segment, PostHog, TikTok...).

    Looks for event/event_type/type/name keys on the body or a batch list.
    """
    if not body:
        return [], {}
    try:
        data = json.loads(body)
    except (ValueError, TypeError):
        return [], {}
    items = data if isinstance(data, list) else (
        data.get("batch") or data.get("events") or [data]
    ) if isinstance(data, dict) else []
    names: List[str] = []
    for item in items:
        if isinstance(item, dict):
            n = item.get("event") or item.get("event_type") or item.get("name")
            if isinstance(n, str):
                names.append(n)
    return names, {}


def parse(vendor: str, url: str, body: Optional[str]) -> Tuple[List[str], Dict[str, Any]]:
    """Dispatch to the right parser for a vendor. Unknown vendors return no events."""
    if vendor == "ga4":
        return parse_ga4(url, body)
    if vendor == "meta_pixel":
        return parse_meta(url)
    if vendor in ("segment", "amplitude", "posthog", "tiktok_pixel", "mixpanel"):
        return parse_json_events(body)
    return [], {}
