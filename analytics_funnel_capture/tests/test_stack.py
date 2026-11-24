"""Tests for tech-stack host labelling."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from funnel_capture.stack import is_first_party, label_host, may_read_form_fields  # noqa: E402


def test_known_hosts_labelled():
    assert label_host("othership.marianaiframes.com") == ("Mariana Tek", "booking")
    assert label_host("cdn.prod.website-files.com") == ("Webflow", "website")
    assert label_host("bookoapp.com") == ("Booko", "dynamic pricing")
    assert label_host("bzrcdn.openai.com") == ("OpenAI pixel", "ads/measurement")
    assert label_host("public.embedreach.com") == ("EmbedReach", "marketing/identity")


def test_unknown_host_is_none():
    assert label_host("totally-new-vendor.example") is None
    assert label_host("") is None


def test_first_party_detection():
    assert is_first_party("www.othership.us", "www.othership.us")
    assert is_first_party("shop.othership.us", "www.othership.us")
    assert not is_first_party("cdn.jsdelivr.net", "www.othership.us")
    # lookalike must not match
    assert not is_first_party("evilothership.us", "www.othership.us")


def test_form_field_heuristic():
    reading = 'document.querySelector(\'[name="bb_email"]\').addEventListener("click", send)'
    assert may_read_form_fields(reading)
    assert not may_read_form_fields("function add(a,b){return a+b}")
    # mentions email but nothing about submit/click handling
    assert not may_read_form_fields("var label = 'type=email'")
