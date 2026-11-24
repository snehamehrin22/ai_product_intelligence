#!/usr/bin/env python3
"""Debug: See what fields Apify actually returns."""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from instagram_hook_analyzer.scraper import InstagramScraper

scraper = InstagramScraper()
run_input = {"profiles": ["garyvee"], "resultsLimit": 1}
run = scraper.client.actor("data-slayer/instagram-profile-reels").call(run_input=run_input)

print("=== First item from Apify ===\n")
for item in scraper.client.dataset(run.default_dataset_id).iterate_items():
    print(json.dumps(dict(item), indent=2))
    break
