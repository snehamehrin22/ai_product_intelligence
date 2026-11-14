"""Building and loading the creator list."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from reel_framework_library.config import CREATORS_CSV
from reel_framework_library.creators import build_creators, load_creators, read_csv_rows

INPUTS = Path(__file__).parent / "inputs"


def test_build_merges_dedupes_and_cleans() -> None:
    """Messy input: '@' prefix, whitespace, case, parens, duplicate across categories."""
    creators = build_creators(
        read_csv_rows(INPUTS / "notion_raw_messy.csv"),
        read_csv_rows(INPUTS / "manual_messy.csv"),
    )
    by_handle = {c.handle: c for c in creators}

    assert list(by_handle) == ["alpha", "beta", "gamma", "delta"]
    assert by_handle["alpha"].notion_category == "Cat A|Cat B"   # one row, both categories
    assert by_handle["beta"].notes == "display name: Beta Name"
    assert by_handle["gamma"].source == "notion"                 # in both sources: stays notion
    assert "also added by hand" in by_handle["gamma"].notes
    assert by_handle["delta"].source == "manual"


def test_build_rejects_empty_handle() -> None:
    """A blank handle must stop the build, not be silently dropped."""
    with pytest.raises(ValueError, match="empty handle"):
        build_creators(read_csv_rows(INPUTS / "notion_raw_empty_handle.csv"), [])


def test_load_valid_file() -> None:
    """A clean file loads in full."""
    assert [c.handle for c in load_creators(INPUTS / "creators_valid.csv").creators] == ["alpha", "beta"]


@pytest.mark.parametrize(
    "filename",
    [
        "creators_at_prefix.csv",
        "creators_trailing_space.csv",
        "creators_parenthetical.csv",
        "creators_uppercase.csv",
        "creators_empty_handle.csv",
        "creators_duplicate.csv",
        "creators_bad_source.csv",
    ],
)
def test_load_rejects_bad_files(filename: str) -> None:
    """The strict model refuses every kind of dirty row the PRD lists."""
    with pytest.raises(ValidationError):
        load_creators(INPUTS / filename)


def test_real_creators_csv_matches_prd() -> None:
    """The committed seed list: 51 valid creators, 47 from Notion plus 4 by hand."""
    creators = load_creators(CREATORS_CSV).creators
    assert len(creators) == 51
    assert sum(c.source == "notion" for c in creators) == 47
    assert {"eyes_of_apoorva", "andrea_mizrahi", "iliya.sharifat", "mi.raga_mi.saga"} <= {
        c.handle for c in creators
    }
