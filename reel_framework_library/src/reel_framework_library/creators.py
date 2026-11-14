"""Creator list handling: clean raw handles, merge sources, load and save the CSV."""

import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .schemas import Creator, CreatorList

_PAREN_SUFFIX = re.compile(r"\s*\(([^)]*)\)\s*$")


def split_display_name(raw: str) -> Tuple[str, str]:
    """Split a Notion creator cell like 'edendotso (eden)' into handle and display name.

    Args:
        raw: The creator text as typed in Notion.

    Returns:
        (handle_part, display_name). display_name is '' when there are no parentheses.
    """
    raw = raw.strip()
    match = _PAREN_SUFFIX.search(raw)
    if not match:
        return raw, ""
    return raw[: match.start()].strip(), match.group(1).strip()


def normalize_handle(raw: str) -> str:
    """Turn a hand-typed handle into the canonical form.

    Notion entries mix '@name', 'name', and 'name (Display Name)'. Cleaning here,
    once, means the strict Creator model can reject anything dirty afterwards.

    Args:
        raw: Handle as typed.

    Returns:
        Lowercase handle with no '@', whitespace, or parenthetical. May be ''.
    """
    handle, _ = split_display_name(raw)
    return handle.strip().lstrip("@").strip().lower()


def build_creators(
    notion_rows: Iterable[Dict[str, str]],
    manual_rows: Iterable[Dict[str, str]],
) -> List[Creator]:
    """Merge Notion rows and hand-added creators into one deduplicated list.

    A creator saved under several Notion categories becomes one row with the
    categories joined by '|'. A creator in both sources stays 'notion' and gets
    a note, so nothing is silently dropped.

    Args:
        notion_rows: Dicts with 'creator' and 'category' keys.
        manual_rows: Dicts with 'handle' and optional 'notes' keys.

    Returns:
        Creators in first-seen order.

    Raises:
        ValueError: If any row has an empty handle (we never skip rows silently).
    """
    merged: Dict[str, Dict[str, object]] = {}

    for row in notion_rows:
        handle = normalize_handle(row["creator"])
        if not handle:
            raise ValueError(f"empty handle in Notion row: {row!r}")
        _, display = split_display_name(row["creator"])
        entry = merged.setdefault(
            handle, {"source": "notion", "categories": [], "notes": []}
        )
        category = row.get("category", "").strip()
        if category and category not in entry["categories"]:
            entry["categories"].append(category)
        if display:
            entry["notes"].append(f"display name: {display}")

    for row in manual_rows:
        handle = normalize_handle(row["handle"])
        if not handle:
            raise ValueError(f"empty handle in manual row: {row!r}")
        note = row.get("notes", "").strip()
        if handle in merged:
            merged[handle]["notes"].append("also added by hand")
        else:
            merged[handle] = {
                "source": "manual",
                "categories": [],
                "notes": [note] if note else [],
            }

    return [
        Creator(
            handle=handle,
            source=entry["source"],
            notion_category="|".join(entry["categories"]),
            notes="; ".join(entry["notes"]),
        )
        for handle, entry in merged.items()
    ]


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    """Read a CSV into a list of dicts."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_creators(creators: List[Creator], path: Path) -> None:
    """Write the creator list to CSV in the column order the PRD specifies."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["handle", "source", "notion_category", "notes"]
        )
        writer.writeheader()
        for creator in creators:
            writer.writerow(creator.model_dump())


def load_creators(path: Path) -> CreatorList:
    """Load creators.csv through the Pydantic models.

    Raises:
        pydantic.ValidationError: On any invalid row, bad handle, or duplicate.
    """
    return CreatorList(creators=[Creator(**row) for row in read_csv_rows(path)])
