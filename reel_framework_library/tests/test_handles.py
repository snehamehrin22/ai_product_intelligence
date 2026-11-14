"""normalize_handle: every messy spelling seen in the Notion export."""

import pytest

from reel_framework_library.creators import normalize_handle, split_display_name


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("@thoughtfully_designed", "thoughtfully_designed"),
        ("aksscameraroll", "aksscameraroll"),
        ("  @Alpha ", "alpha"),                    # whitespace + case + prefix together
        ("edendotso (eden)", "edendotso"),         # Notion 'handle (display name)' form
        ("hellocherrymedia (Vritika)", "hellocherrymedia"),
        ("@host___office", "host___office"),       # underscores are legal and kept
        ("jade.got.curious", "jade.got.curious"),  # periods are legal and kept
        ("", ""),
        ("@", ""),
        ("   ", ""),
    ],
)
def test_normalize_handle(raw: str, expected: str) -> None:
    """Cleaning is idempotent in effect and never raises."""
    assert normalize_handle(raw) == expected


def test_normalize_is_idempotent() -> None:
    """Normalizing twice gives the same answer as once."""
    once = normalize_handle("@Some.Name (Display)")
    assert normalize_handle(once) == once


def test_split_display_name() -> None:
    """Display name is kept for the notes column instead of being thrown away."""
    assert split_display_name("inzeenius (Zenia A)") == ("inzeenius", "Zenia A")
    assert split_display_name("plain") == ("plain", "")
