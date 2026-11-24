"""Tests for mobile vendor rules, Mixpanel parsing, and the mitmproxy logger."""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from funnel_capture.vendors import classify, parse  # noqa: E402


def test_mobile_vendors_classified():
    assert classify("https://app-measurement.com/a") == "firebase"
    assert classify("https://gcdsdk.appsflyer.com/install_data/v4.0/id1") == "appsflyer"
    assert classify("https://app.adjust.com/session") == "adjust"
    assert classify("https://api.revenuecat.com/v1/subscribers/x") == "revenuecat"
    assert classify("https://sdk.iad-01.braze.com/api/v3/data") == "braze"


def test_amplitude_mobile_body():
    body = json.dumps({"api_key": "k", "events": [{"event_type": "onboarding_step_1"}, {"event_type": "paywall_shown"}]})
    names, _ = parse("amplitude", "https://api2.amplitude.com/2/httpapi", body)
    assert names == ["onboarding_step_1", "paywall_shown"]


def test_mixpanel_base64_form_body():
    payload = json.dumps([{"event": "Signup Started", "properties": {}}]).encode()
    body = "data=" + base64.b64encode(payload).decode()
    names, _ = parse("mixpanel", "https://api.mixpanel.com/track", body)
    assert names == ["Signup Started"]


def test_mixpanel_bad_base64_is_safe():
    assert parse("mixpanel", "https://api.mixpanel.com/track", "data=%%%") == ([], {})


def test_mitm_logger_writes_tagged_jsonl(tmp_path):
    from mitmproxy.test import tflow, tutils
    from funnel_capture.mitm_logger import AnalyticsLogger

    out, step = tmp_path / "out.jsonl", tmp_path / "step.txt"
    step.write_text("paywall")
    logger = AnalyticsLogger(out, step)

    flow = tflow.tflow(resp=True)
    flow.request = tutils.treq(
        host="api2.amplitude.com", port=443, scheme=b"https", authority=b"",
        path=b"/2/httpapi", method=b"POST",
        content=json.dumps({"events": [{"event_type": "paywall_shown"}]}).encode(),
    )
    logger.response(flow)

    # A non-analytics request must be ignored
    other = tflow.tflow(resp=True)
    other.request = tutils.treq(host="api.example.com", scheme=b"https", authority=b"", path=b"/x")
    logger.response(other)

    rows = [json.loads(l) for l in out.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["vendor"] == "amplitude"
    assert rows[0]["event_names"] == ["paywall_shown"]
    assert rows[0]["step"] == "paywall"
    assert rows[0]["frame_url"] == "ios-app"


def test_mitm_logger_unmarked_when_no_step_file(tmp_path):
    from funnel_capture.mitm_logger import AnalyticsLogger

    logger = AnalyticsLogger(tmp_path / "o.jsonl", tmp_path / "missing.txt")
    assert logger._current_step() == "unmarked"
