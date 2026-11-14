"""Build data/creators.csv from the Notion export plus hand-added creators.

Re-run whenever data/seed/*.csv changes. Fails loudly on any bad row.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import (  # noqa: E402
    CREATORS_CSV,
    MANUAL_CREATORS_CSV,
    NOTION_RAW_CSV,
)
from reel_framework_library.creators import (  # noqa: E402
    build_creators,
    load_creators,
    read_csv_rows,
    write_creators,
)


def main() -> int:
    """Merge seed files, write creators.csv, then reload it to prove it validates."""
    creators = build_creators(read_csv_rows(NOTION_RAW_CSV), read_csv_rows(MANUAL_CREATORS_CSV))
    write_creators(creators, CREATORS_CSV)

    reloaded = load_creators(CREATORS_CSV).creators
    notion = sum(1 for c in reloaded if c.source == "notion")
    manual = sum(1 for c in reloaded if c.source == "manual")
    print(f"Wrote {len(reloaded)} creators to {CREATORS_CSV} ({notion} notion, {manual} manual)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
