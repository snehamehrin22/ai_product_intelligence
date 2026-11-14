"""Transcription logic with a fake OpenAI client and fake downloader: free and offline."""

import json
from types import SimpleNamespace

import pytest

from reel_framework_library.transcribe import (
    estimate_cost,
    load_audio_urls,
    pending,
    queue_from_scored,
    to_transcript,
    transcribe_all,
)

WHISPER_REPLY = {
    "language": "english",
    "duration": 12.5,
    "text": " Why do elevators have mirrors? ",
    "segments": [
        {"start": 0.0, "end": 4.0, "text": " Why do elevators have mirrors?", "no_speech_prob": 0.01, "avg_logprob": -0.2},
        {"start": 4.0, "end": 12.0, "text": " Because waiting felt long.", "no_speech_prob": 0.02, "avg_logprob": -0.3},
    ],
}


class FakeOpenAI:
    """Returns a canned Whisper reply, or raises for a chosen shortcode."""

    def __init__(self, fail_for=None):
        self.fail_for = fail_for
        self.calls = []
        self.audio = SimpleNamespace(transcriptions=SimpleNamespace(create=self._create))

    def _create(self, model, file, response_format):
        self.calls.append((model, file[0], response_format))
        if self.fail_for and file[0].startswith(self.fail_for):
            raise RuntimeError("boom")
        return dict(WHISPER_REPLY)


ROWS = [
    {"handle": "a", "shortcode": "lo", "outlier_ratio": "0.5", "duration_seconds": "60"},
    {"handle": "a", "shortcode": "new", "outlier_ratio": "", "duration_seconds": "30"},
    {"handle": "b", "shortcode": "hi", "outlier_ratio": "9.0", "duration_seconds": "90"},
]
URLS = {("a", "lo"): "u1", ("a", "new"): "u2", ("b", "hi"): "u3"}


def test_to_transcript_validates_and_strips() -> None:
    """The reply becomes a typed Transcript with timed segments."""
    t = to_transcript("a", "x", "whisper-1", WHISPER_REPLY)
    assert t.text == "Why do elevators have mirrors?"
    assert len(t.segments) == 2 and t.segments[1].start == 4.0
    assert t.language == "english"


def test_malformed_reply_is_rejected() -> None:
    """A segment missing timestamps must fail loudly, not be saved half-empty."""
    with pytest.raises(Exception):
        to_transcript("a", "x", "whisper-1", {"text": "hi", "segments": [{"text": "no times"}]})


def test_queue_orders_best_first_and_young_last(tmp_path) -> None:
    """Interrupted runs should have finished the most useful reels."""
    csv_path = tmp_path / "scored.csv"
    csv_path.write_text("handle,shortcode,outlier_ratio,duration_seconds\n" + "\n".join(
        f"{r['handle']},{r['shortcode']},{r['outlier_ratio']},{r['duration_seconds']}" for r in ROWS))
    assert [r["shortcode"] for r in queue_from_scored(csv_path)] == ["hi", "lo", "new"]


def test_estimate_cost() -> None:
    """180 seconds of audio is 3 minutes."""
    assert estimate_cost(ROWS, 0.006) == (3.0, 0.02)


def test_transcribe_all_saves_one_file_per_reel_and_resumes(tmp_path) -> None:
    """Saved transcripts are skipped next time, so nothing is paid for twice."""
    client = FakeOpenAI()
    result = transcribe_all(client, "whisper-1", ROWS, URLS, tmp_path / "t", tmp_path / "e.jsonl",
                            workers=2, downloader=lambda url: b"audio")
    assert result["done"] == 3 and result["failed"] == []
    assert (tmp_path / "t" / "b" / "hi.json").exists()
    assert json.loads((tmp_path / "t" / "a" / "lo.json").read_text())["segments"][0]["end"] == 4.0
    assert all(call[2] == "verbose_json" for call in client.calls)
    assert pending(ROWS, tmp_path / "t") == []


def test_failure_is_logged_and_does_not_stop_the_run(tmp_path) -> None:
    """One bad reel must not lose the other transcripts."""
    result = transcribe_all(FakeOpenAI(fail_for="lo"), "whisper-1", ROWS, URLS, tmp_path / "t",
                            tmp_path / "e.jsonl", workers=2, downloader=lambda url: b"audio")
    assert result["done"] == 2 and result["failed"] == ["lo"]
    errors = [json.loads(l) for l in (tmp_path / "e.jsonl").read_text().splitlines()]
    assert errors[0]["shortcode"] == "lo" and errors[0]["stage"] == "transcribe"
    assert not (tmp_path / "t" / "a" / "lo.json").exists()


def test_download_failure_is_logged(tmp_path) -> None:
    """Expired CDN links raise on download; that's an error record."""
    def expired(url):
        raise RuntimeError("403 expired")
    result = transcribe_all(FakeOpenAI(), "whisper-1", ROWS[:1], URLS, tmp_path / "t",
                            tmp_path / "e.jsonl", downloader=expired)
    assert result["failed"] == ["lo"]


def test_missing_audio_url_is_counted(tmp_path) -> None:
    """A reel with no audio URL is reported, not silently skipped."""
    result = transcribe_all(FakeOpenAI(), "whisper-1", ROWS, {("b", "hi"): "u3"}, tmp_path / "t",
                            tmp_path / "e.jsonl", downloader=lambda u: b"x")
    assert result["done"] == 1 and result["skipped_no_audio"] == 2


def test_load_audio_urls(tmp_path) -> None:
    """Audio URLs come from the raw scraper files, keyed by creator and shortcode."""
    (tmp_path / "a.json").write_text(json.dumps([{"shortCode": "s1", "audioUrl": "http://x"}, {"shortCode": "s2"}]))
    assert load_audio_urls(tmp_path) == {("a", "s1"): "http://x"}
