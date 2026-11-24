#!/usr/bin/env python3
"""Test the Instagram scraper with one creator."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from instagram_hook_analyzer.scraper import InstagramScraper

def main():
    """Test scraper with a simple creator."""
    print("=== Testing Instagram Scraper ===\n")

    # Test with a well-known creator
    test_username = input("Enter Instagram username to test (e.g., garyvee, hubermanlab): ").strip()

    if not test_username:
        print("No username provided. Using 'garyvee' as test.")
        test_username = "garyvee"

    try:
        scraper = InstagramScraper()
        print(f"\nFetching top 5 reels from @{test_username}...\n")

        reels = scraper.get_viral_reels(test_username, max_reels=5)

        if reels:
            print(f"\n✅ Found {len(reels)} reels!\n")
            print("Top 3 reels by views:")
            for i, reel in enumerate(reels[:3], 1):
                print(f"\n{i}. {reel['shortcode']}")
                print(f"   Views: {reel['views']:,}")
                print(f"   Likes: {reel['likes']:,}")
                print(f"   URL: {reel['url']}")
                print(f"   Caption: {reel['caption'][:80]}..." if len(reel['caption']) > 80 else f"   Caption: {reel['caption']}")

            print("\n✅ Scraper test PASSED!")
            print("Ready to run full analysis.")

        else:
            print("❌ No reels found. Check the username.")

    except Exception as e:
        print(f"\n❌ Scraper test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
