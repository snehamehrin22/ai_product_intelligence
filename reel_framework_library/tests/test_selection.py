"""Speech detection and top-per-creator selection."""

from pathlib import Path

from reel_framework_library.schemas import Transcript, TranscriptSegment
from reel_framework_library.selection import has_speech, select_top, speech_metrics


def _t(text_words: int, spans, handle="a", shortcode="x") -> Transcript:
    return Transcript(
        handle=handle, shortcode=shortcode, model="whisper-1", language="english",
        text=" ".join(["word"] * text_words),
        segments=[TranscriptSegment(start=s, end=e, text="t") for s, e in spans],
    )


def test_continuous_narration_has_speech() -> None:
    """60s reel, speech across all of it, 200 words: a talking reel."""
    m = speech_metrics(_t(200, [(0, 30), (30, 60)]), 60)
    assert m["coverage"] == 1.0 and m["words_per_minute"] == 200
    assert has_speech(m)


def test_sparse_text_fails_on_words_per_minute() -> None:
    """Seen in the data: 60s reel with 5 words of hallucinated text."""
    assert not has_speech(speech_metrics(_t(5, [(0, 50)]), 60))


def test_short_clip_fails_on_word_count() -> None:
    """A 7-second loop repeating three words has a high rate but nothing to learn from."""
    assert not has_speech(speech_metrics(_t(12, [(0, 7)]), 7))


def test_low_coverage_fails() -> None:
    """Speech in 20% of the video is not a talking reel even at a fast rate."""
    assert not has_speech(speech_metrics(_t(200, [(0, 12)]), 60))


def test_missing_transcript_is_no_speech() -> None:
    """The 11 reels with no audio link must not crash and must not be selected."""
    assert not has_speech(speech_metrics(None, 30))


def test_coverage_capped_at_one() -> None:
    """Overlapping segments can sum past the duration."""
    assert speech_metrics(_t(200, [(0, 40), (30, 70)]), 60)["coverage"] == 1.0


def _row(handle, code, ratio, eligible=True, speech=True):
    return {
        "handle": handle, "shortcode": code, "url": f"u/{code}", "posted_at": "t", "views": 1,
        "likes": 1, "comments": 1, "followers": 1, "duration_seconds": "60", "outlier_ratio": str(ratio),
        "creator_median_views": 1, "creator_low_sample": False, "coverage": 1.0, "words": 200,
        "words_per_minute": 200, "language": "english", "eligible": str(eligible), "has_speech": speech,
    }


def test_select_ranks_within_creator_and_skips_ineligible_and_no_speech() -> None:
    """Top N per creator by ratio; young and silent reels never selected."""
    table = [
        _row("a", "a1", 5.0), _row("a", "a2", 9.0), _row("a", "a3", 2.0),
        _row("a", "young", 99.0, eligible=False), _row("a", "mute", 50.0, speech=False),
        _row("b", "b1", 1000.0),
    ]
    picked = select_top(table, 2, Path("t"))
    a = [r["shortcode"] for r in picked if r["handle"] == "a"]
    assert a == ["a2", "a1"]                       # best first, capped at 2, no young/mute
    assert [r["rank_in_creator"] for r in picked if r["handle"] == "a"] == [1, 2]
    assert [r["shortcode"] for r in picked if r["handle"] == "b"] == ["b1"]


def test_creator_with_nothing_eligible_is_absent() -> None:
    """A creator with no qualifying reels yields no rows (reported as a shortfall)."""
    assert select_top([_row("c", "c1", 3.0, speech=False)], 10, Path("t")) == []
