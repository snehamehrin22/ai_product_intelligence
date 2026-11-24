"""Main orchestration for Instagram hook analysis."""

from typing import List, Dict
import pandas as pd
from pathlib import Path

from .scraper import InstagramScraper
from .video_processor import VideoProcessor
from .hook_analyzer import HookAnalyzerAI


class HookAnalyzer:
    """Orchestrates the full hook analysis pipeline."""

    def __init__(self):
        """Initialize all components."""
        self.scraper = InstagramScraper()
        self.video_processor = VideoProcessor()
        self.hook_analyzer = HookAnalyzerAI()

    def analyze_creators(
        self,
        usernames: List[str],
        max_reels_per_creator: int = 10,
        output_path: str = "output/hooks_analysis.csv"
    ) -> pd.DataFrame:
        """
        Analyze hooks from multiple creators.

        Args:
            usernames: List of Instagram usernames
            max_reels_per_creator: Max reels to analyze per creator
            output_path: Where to save results CSV

        Returns:
            DataFrame with analysis results
        """
        # Step 1: Scrape reels
        print("\n=== STEP 1: Scraping Instagram Reels ===")
        reels = self.scraper.get_reels_from_multiple_creators(
            usernames,
            max_reels_per_creator
        )

        if not reels:
            print("No reels found!")
            return pd.DataFrame()

        # Step 2: Process videos and extract hooks
        print("\n=== STEP 2: Extracting Hooks (OCR + Transcription) ===")
        results = []

        for i, reel in enumerate(reels, 1):
            print(f"\n[{i}/{len(reels)}] Processing @{reel['username']}/{reel['shortcode']}")

            # Extract hook data
            hook_data = self.video_processor.extract_hook_data(
                reel['video_url'],
                reel['shortcode']
            )

            if not hook_data['combined_hook']:
                print(f"Skipping {reel['shortcode']} - no hook data extracted")
                continue

            # Step 3: Analyze with GPT-4o
            print(f"Analyzing reel structure (hook + framework + CTA) with GPT-4o...")
            analysis = self.hook_analyzer.analyze_hook(
                hook_text=hook_data['combined_hook'],
                full_transcript=hook_data['full_transcript'],
                engagement={
                    'views': reel['views'],
                    'likes': reel['likes'],
                    'comments': reel['comments']
                },
                caption=reel['caption']
            )

            # Combine all data
            result = {
                'creator_username': reel['username'],
                'reel_shortcode': reel['shortcode'],
                'reel_url': reel['url'],
                'views': reel['views'],
                'likes': reel['likes'],
                'comments': reel['comments'],
                'duration_seconds': reel['duration'],
                'posted_date': reel['timestamp'],
                'caption': reel['caption'],
                'hook_ocr': hook_data['hook_ocr'],
                'full_transcript': hook_data['full_transcript'],
                'hook_pattern': analysis.get('hook_pattern', 'unknown'),
                'hook_text_extracted': analysis.get('hook_text_extracted', ''),
                'hook_score': analysis.get('hook_score', 0),
                'body_framework': analysis.get('body_framework', 'unknown'),
                'body_summary': analysis.get('body_summary', ''),
                'cta_type': analysis.get('cta_type', 'none'),
                'cta_text_extracted': analysis.get('cta_text_extracted', ''),
                'what_works': analysis.get('what_works', ''),
                'what_fails': analysis.get('what_fails', ''),
                'key_takeaway': analysis.get('key_takeaway', '')
            }

            results.append(result)

            # Save incrementally (in case of crashes)
            df = pd.DataFrame(results)
            Path(output_path).parent.mkdir(exist_ok=True)
            df.to_csv(output_path, index=False)
            print(f"Saved to {output_path}")

        # Final results
        print(f"\n=== ANALYSIS COMPLETE ===")
        print(f"Analyzed {len(results)} reels")
        print(f"Results saved to: {output_path}")

        return pd.DataFrame(results)

    def get_top_hooks_by_pattern(
        self,
        df: pd.DataFrame,
        pattern: str = None,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Get top-performing hooks, optionally filtered by pattern.

        Args:
            df: Results DataFrame
            pattern: Hook pattern to filter (optional)
            top_n: Number of top hooks to return

        Returns:
            Filtered and sorted DataFrame
        """
        if pattern:
            df = df[df['hook_pattern'] == pattern]

        return df.nlargest(top_n, 'hook_score')
