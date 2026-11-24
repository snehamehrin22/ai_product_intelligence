"""Tests for vendor classification and event parsing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from funnel_capture.vendors import classify, parse  # noqa: E402

GA4 = "https://analytics.google.com/g/collect?v=2&tid=G-TEST&dl=https%3A%2F%2Fx.com%2F&en=scroll&epn.percent_scrolled=90"


def test_classify_known_vendors():
    assert classify(GA4) == "ga4"
    assert classify("https://www.facebook.com/tr?id=1&ev=PageView") == "meta_pixel"
    assert classify("https://r.clarity.ms/collect") == "clarity"
    assert classify("https://px.ads.linkedin.com/collect?v=2") == "linkedin"


def test_classify_ignores_non_analytics():
    assert classify("https://www.othership.us/schedule") is None
    assert classify("https://www.google.com/search?q=x") is None  # not an ads/analytics path
    assert classify("chrome-extension://abc/index.js") is None


def test_ga4_batch_body_has_multiple_events():
    body = "en=page_view&ep.page_type=home\nen=begin_checkout&epn.value=45&ep.currency=USD"
    names, props = parse("ga4", GA4, body)
    assert names == ["scroll", "page_view", "begin_checkout"]
    assert props["begin_checkout#2.epn.value"] == "45"
    assert props["tid"] == "G-TEST"


def test_ga4_empty_body():
    names, _ = parse("ga4", GA4, None)
    assert names == ["scroll"]


def test_meta_event_name_and_custom_data():
    url = "https://www.facebook.com/tr?id=99&ev=InitiateCheckout&cd[value]=45&cd[currency]=USD"
    names, props = parse("meta_pixel", url, None)
    assert names == ["InitiateCheckout"]
    assert props["cd[value]"] == "45"


def test_json_batch_events():
    body = '{"batch":[{"event":"Signup Started"},{"event":"Paywall Viewed"}]}'
    names, _ = parse("segment", "https://api.segment.io/v1/batch", body)
    assert names == ["Signup Started", "Paywall Viewed"]


def test_malformed_json_returns_empty():
    assert parse("segment", "https://api.segment.io/v1/t", "{not json") == ([], {})
