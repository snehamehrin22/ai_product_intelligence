#!/usr/bin/env python3
"""Scrape a creator's reels into a CSV.

Usage:
    python scripts/scrape_creator.py andrea_mizrahi [--limit 20]
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from instagram_hook_analyzer.scraper import fetch_reels
from instagram_hook_analyzer.transcribe import split_hook_body


def main() -> None:
    """Fetch reels, transcribe each, and save output/<username>_reels.csv."""
    p = argparse.ArgumentParser()
    p.add_argument("username")
    p.add_argument("--limit", type=int, default=20)
    args = p.parse_args()
    username = args.username.strip().lstrip("@")

    reels = fetch_reels(username, args.limit)
    print(f"Fetched {len(reels)} reels for @{username}")
    for i, r in enumerate(reels, 1):
        r.update(split_hook_body(r.pop("audio_url")))
        print(f"[{i}/{len(reels)}] {r['url']} {'ERR ' + r['error'] if r['error'] else 'ok'}")

    out = Path(__file__).parent.parent / "output" / f"{username}_reels.csv"
    pd.DataFrame(reels).to_csv(out, index=False)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
