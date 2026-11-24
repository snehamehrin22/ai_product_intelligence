#!/usr/bin/env python3
"""
Main script to analyze Instagram creator hooks.

Usage:
    python scripts/analyze_creators.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from instagram_hook_analyzer import HookAnalyzer


def main():
    """Run hook analysis on Instagram creators."""

    print("=== Instagram Hook Analyzer ===\n")

    # Get creator usernames
    print("Enter Instagram usernames to analyze (comma-separated):")
    print("Example: creatorone, creatortwo, creatorthree\n")

    usernames_input = input("Usernames: ").strip()

    if not usernames_input:
        print("No usernames provided. Exiting.")
        return

    # Parse usernames
    usernames = [u.strip().replace('@', '') for u in usernames_input.split(',')]

    print(f"\nAnalyzing creators: {', '.join(usernames)}")

    # Get max reels per creator
    max_reels_input = input("\nMax reels per creator (default 10): ").strip()
    max_reels = int(max_reels_input) if max_reels_input else 10

    # Run analysis
    analyzer = HookAnalyzer()

    results = analyzer.analyze_creators(
        usernames=usernames,
        max_reels_per_creator=max_reels,
        output_path="output/hooks_analysis.csv"
    )

    if not results.empty:
        print("\n=== TOP HOOKS BY SCORE ===")
        top_hooks = results.nlargest(5, 'hook_score')[
            ['creator_username', 'hook_score', 'hook_pattern', 'combined_hook']
        ]
        print(top_hooks.to_string(index=False))

        print("\n=== PATTERN DISTRIBUTION ===")
        pattern_counts = results['hook_pattern'].value_counts()
        print(pattern_counts)

        print(f"\nFull results saved to: output/hooks_analysis.csv")
        print("Open in Excel/Google Sheets for detailed analysis")


if __name__ == "__main__":
    main()
