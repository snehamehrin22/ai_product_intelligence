"""Instagram Reel scraper using Apify."""

import os
from typing import List, Dict
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()


class InstagramScraper:
    """Scrapes Instagram Reels using Apify."""

    def __init__(self, api_key: str = None):
        """Initialize scraper with Apify API key."""
        self.api_key = api_key or os.getenv("APIFY_API_KEY")
        if not self.api_key:
            raise ValueError("APIFY_API_KEY not found in environment")
        self.client = ApifyClient(self.api_key)

    def get_viral_reels(
        self,
        username: str,
        max_reels: int = 20
    ) -> List[Dict]:
        """
        Get best-performing reels from an Instagram creator.

        Args:
            username: Instagram username (without @)
            max_reels: Maximum number of reels to fetch

        Returns:
            List of reel data dictionaries, sorted by views (most viral first)
        """
        print(f"Fetching best-performing reels from @{username}...")

        # Using apify/instagram-reel-scraper (works for all profiles)
        run_input = {
            "username": [username],
            "resultsLimit": max_reels
        }

        # Run the Actor and wait for it to finish
        run = self.client.actor("apify/instagram-reel-scraper").call(run_input=run_input)

        # Fetch results from the run's dataset
        reels = []
        for item in self.client.dataset(run.default_dataset_id).iterate_items():
            # apify/instagram-reel-scraper format
            reels.append({
                "username": username,
                "shortcode": item.get("shortCode", ""),
                "url": item.get("url", ""),
                "video_url": item.get("videoUrl", ""),
                "caption": item.get("caption", ""),
                "views": item.get("videoViewCount") or item.get("videoPlayCount") or 0,
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "duration": item.get("videoDuration", 0),
                "timestamp": item.get("timestamp", ""),
            })

        # Filter out reels with no video URL and sort by views
        reels = [r for r in reels if r.get("video_url")]
        reels.sort(key=lambda x: x.get("views") or 0, reverse=True)

        print(f"Found {len(reels)} reels from @{username}")
        return reels

    def get_reels_from_multiple_creators(
        self,
        usernames: List[str],
        max_reels_per_creator: int = 20
    ) -> List[Dict]:
        """
        Get viral reels from multiple creators.

        Args:
            usernames: List of Instagram usernames
            max_reels_per_creator: Max reels per creator

        Returns:
            Combined list of reels from all creators
        """
        all_reels = []

        for username in usernames:
            try:
                reels = self.get_viral_reels(username, max_reels_per_creator)
                all_reels.extend(reels)
            except Exception as e:
                print(f"Error fetching reels from @{username}: {e}")
                continue

        print(f"\nTotal reels collected: {len(all_reels)}")
        return all_reels


def fetch_reels(username: str, limit: int = 20) -> List[Dict]:
    """Fetch the latest reels for a creator with engagement metrics.

    Args:
        username: Instagram username without the @.
        limit: Number of reels to fetch.

    Returns:
        One flat dict per reel. Saves and reshares are not returned by the
        Apify actor, so they are not included.
    """
    scraper = InstagramScraper()
    run = scraper.client.actor("apify/instagram-reel-scraper").call(
        run_input={"username": [username], "resultsLimit": limit}
    )
    reels = []
    for item in scraper.client.dataset(run.default_dataset_id).iterate_items():
        reels.append({
            "username": username,
            "url": item.get("url", ""),
            "posted_at": item.get("timestamp", ""),
            "duration_s": item.get("videoDuration"),
            # videoPlayCount is the populated views field; videoViewCount is None.
            "views": item.get("videoPlayCount"),
            "likes": item.get("likesCount"),
            "comments": item.get("commentsCount"),
            "caption": item.get("caption", ""),
            # audioUrl is ~1MB vs 25MB+ for the video, so it stays under Whisper's limit.
            "audio_url": item.get("audioUrl", ""),
        })
    return reels
