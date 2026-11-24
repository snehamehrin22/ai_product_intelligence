#!/usr/bin/env python3
"""
Analyze @thoughtfully_designed Instagram Reels.

Gets top 20 reels by engagement, extracts:
- Hook (first 5 seconds)
- Body framework
- CTA
- Full transcript
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from instagram_hook_analyzer import HookAnalyzer

def main():
    """Analyze thoughtfully_designed reels."""
    print("=== Analyzing @thoughtfully_designed ===\n")

    analyzer = HookAnalyzer()

    # Start with 3 reels to test, then scale to 20
    test_mode = input("Test mode (3 reels) or full (20 reels)? [test/full]: ").strip().lower()
    max_reels = 3 if test_mode == "test" else 20

    print(f"\nAnalyzing top {max_reels} reels from @thoughtfully_designed")
    print("This will:")
    print("  1. Scrape best-performing reels")
    print("  2. Download videos")
    print("  3. Extract transcripts (Whisper)")
    print("  4. Analyze hook + framework + CTA (GPT-4o)")
    print(f"\nEstimated cost: ~${max_reels * 0.02:.2f}")
    print("Estimated time: ~{} minutes\n".format(max_reels * 2))

    proceed = input("Proceed? [y/n]: ").strip().lower()
    if proceed != 'y':
        print("Cancelled.")
        return

    # Run analysis
    results = analyzer.analyze_creators(
        usernames=["thoughtfully_designed"],
        max_reels_per_creator=max_reels,
        output_path="output/thoughtfully_designed_analysis.csv"
    )

    if not results.empty:
        print("\n=== ANALYSIS SUMMARY ===")
        print(f"\nTotal reels analyzed: {len(results)}")

        print("\n--- Hook Patterns ---")
        print(results['hook_pattern'].value_counts())

        print("\n--- Body Frameworks ---")
        print(results['body_framework'].value_counts())

        print("\n--- CTA Types ---")
        print(results['cta_type'].value_counts())

        print("\n--- Top 5 by Hook Score ---")
        top_5 = results.nlargest(5, 'hook_score')[
            ['reel_url', 'hook_score', 'hook_pattern', 'body_framework', 'cta_type', 'views']
        ]
        print(top_5.to_string(index=False))

        print(f"\n\nFull results saved to: output/thoughtfully_designed_analysis.csv")
        print("Open in Excel/Google Sheets for detailed analysis")

if __name__ == "__main__":
    main()
