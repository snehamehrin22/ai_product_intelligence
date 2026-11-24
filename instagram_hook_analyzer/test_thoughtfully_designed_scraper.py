#!/usr/bin/env python3
"""Test scraping thoughtfully_designed specifically."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from instagram_hook_analyzer.scraper import InstagramScraper
import json

scraper = InstagramScraper()

# Test different Apify actors to see which works
print("Testing different Apify scrapers for @thoughtfully_designed...\n")

# Try 1: apify/instagram-scraper
print("=== Try 1: apify/instagram-scraper ===")
try:
    run = scraper.client.actor("apify/instagram-scraper").call(run_input={
        "usernames": ["thoughtfully_designed"],
        "resultsLimit": 5,
        "resultsType": "posts"
    })
    count = 0
    for item in scraper.client.dataset(run.default_dataset_id).iterate_items():
        count += 1
        if count == 1:
            print(f"✓ Got {count} item")
            print(f"Sample: {json.dumps(dict(item))[:200]}...")
    print(f"Total: {count} items\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")

# Try 2: Different actor
print("=== Try 2: apify/instagram-reel-scraper ===")
try:
    run = scraper.client.actor("apify/instagram-reel-scraper").call(run_input={
        "username": ["thoughtfully_designed"],
        "resultsLimit": 5
    })
    count = 0
    for item in scraper.client.dataset(run.default_dataset_id).iterate_items():
        count += 1
    print(f"Total: {count} items\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")
