"""
Sentiment analysis and behavioral keyword detection.

Detects retention signals, churn language, and behavioral patterns in reviews.
"""

import re
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime

from .schemas import (
    Review, ReviewBatch, RetentionSignal, SignalSummary, KeywordConfig
)


class SentimentAnalyzer:
    """Analyzes reviews for behavioral signals and patterns."""

    def __init__(self, keyword_config: KeywordConfig = None):
        """
        Initialize analyzer with keyword configuration.

        Args:
            keyword_config: Custom keyword configuration (uses defaults if None)
        """
        self.config = keyword_config or KeywordConfig()

    def analyze_review_batch(self, batch: ReviewBatch) -> List[RetentionSignal]:
        """
        Analyze a batch of reviews for behavioral signals.

        Args:
            batch: ReviewBatch to analyze

        Returns:
            List of detected RetentionSignals
        """
        signals = []

        for review in batch.reviews:
            review_signals = self.detect_signals_in_review(review)
            signals.extend(review_signals)

        return signals

    def detect_signals_in_review(self, review: Review) -> List[RetentionSignal]:
        """
        Detect all behavioral signals in a single review.

        Args:
            review: Review to analyze

        Returns:
            List of RetentionSignals found
        """
        signals = []
        text_lower = review.text.lower()

        # Check each signal type
        signal_checks = [
            ("loyalty", self.config.loyalty_keywords),
            ("churn", self.config.churn_keywords),
            ("first_timer", self.config.first_timer_keywords),
            ("repeat", self.config.repeat_keywords),
            ("onboarding_issue", self.config.onboarding_issue_keywords),
            ("pricing_mention", self.config.pricing_keywords),
            ("social_mention", self.config.social_keywords),
        ]

        for signal_type, keywords in signal_checks:
            matches = self._find_keyword_matches(text_lower, keywords)

            if matches:
                # Extract relevant excerpt (sentence containing the keyword)
                excerpt = self._extract_excerpt(review.text, matches[0])

                signal = RetentionSignal(
                    signal_type=signal_type,
                    keywords=matches,
                    excerpt=excerpt,
                    review_rating=review.rating,
                    review_date=review.date,
                    cafe_name=review.cafe_name
                )

                signals.append(signal)

        return signals

    def _find_keyword_matches(self, text: str, keywords: List[str]) -> List[str]:
        """
        Find all matching keywords in text.

        Args:
            text: Text to search (already lowercased)
            keywords: List of keywords to find

        Returns:
            List of matched keywords
        """
        matches = []

        for keyword in keywords:
            # Use word boundary matching to avoid partial matches
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                matches.append(keyword)

        return matches

    def _extract_excerpt(self, text: str, keyword: str, context_chars: int = 100) -> str:
        """
        Extract an excerpt around a keyword.

        Args:
            text: Full review text
            keyword: Keyword to extract around
            context_chars: Characters of context on each side

        Returns:
            Excerpt containing the keyword with context
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        # Find keyword position
        pos = text_lower.find(keyword_lower)

        if pos == -1:
            # Keyword not found, return first N chars
            return text[:context_chars * 2] + "..."

        # Extract excerpt with context
        start = max(0, pos - context_chars)
        end = min(len(text), pos + len(keyword) + context_chars)

        excerpt = text[start:end].strip()

        # Add ellipsis if we truncated
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."

        return excerpt

    def summarize_signals(self, signals: List[RetentionSignal]) -> List[SignalSummary]:
        """
        Summarize signals by type.

        Args:
            signals: List of all detected signals

        Returns:
            List of SignalSummary objects grouped by type
        """
        if not signals:
            return []

        # Group by cafe and signal type
        grouped = defaultdict(lambda: defaultdict(list))

        for signal in signals:
            key = (signal.cafe_name, signal.signal_type)
            grouped[signal.cafe_name][signal.signal_type].append(signal)

        # Create summaries
        summaries = []

        for cafe_name, signal_groups in grouped.items():
            for signal_type, signal_list in signal_groups.items():
                # Collect all keywords and excerpts
                all_keywords = []
                all_excerpts = []

                for signal in signal_list:
                    all_keywords.extend(signal.keywords)
                    all_excerpts.append(signal.excerpt)

                # Deduplicate keywords, keep unique excerpts (up to 5)
                unique_keywords = list(set(all_keywords))
                sample_excerpts = all_excerpts[:5]  # Max 5 samples

                summary = SignalSummary(
                    cafe_name=cafe_name,
                    signal_type=signal_type,
                    count=len(signal_list),
                    sample_excerpts=sample_excerpts,
                    keywords_found=unique_keywords
                )

                summaries.append(summary)

        # Sort by count (most frequent first)
        summaries.sort(key=lambda x: x.count, reverse=True)

        return summaries

    def get_sentiment_distribution(self, batch: ReviewBatch) -> Dict[str, int]:
        """
        Get distribution of review ratings.

        Args:
            batch: ReviewBatch to analyze

        Returns:
            Dict mapping sentiment to count
        """
        distribution = {
            "5_star": 0,
            "4_star": 0,
            "3_star": 0,
            "2_star": 0,
            "1_star": 0
        }

        for review in batch.reviews:
            distribution[f"{review.rating}_star"] += 1

        return distribution

    def identify_critical_issues(
        self,
        signals: List[RetentionSignal],
        min_mentions: int = 3
    ) -> List[Tuple[str, int, List[str]]]:
        """
        Identify critical issues mentioned multiple times.

        Args:
            signals: List of detected signals
            min_mentions: Minimum mentions to be considered critical

        Returns:
            List of (issue_type, count, sample_excerpts)
        """
        # Focus on negative signals
        negative_signals = [
            s for s in signals
            if s.signal_type in ["churn", "onboarding_issue"] or s.review_rating <= 2
        ]

        # Group by signal type
        grouped = defaultdict(list)
        for signal in negative_signals:
            grouped[signal.signal_type].append(signal)

        # Filter by minimum mentions
        critical = []
        for signal_type, signal_list in grouped.items():
            if len(signal_list) >= min_mentions:
                excerpts = [s.excerpt for s in signal_list[:5]]  # Max 5 samples
                critical.append((signal_type, len(signal_list), excerpts))

        # Sort by frequency
        critical.sort(key=lambda x: x[1], reverse=True)

        return critical

    def identify_strengths(
        self,
        signals: List[RetentionSignal],
        min_mentions: int = 3
    ) -> List[Tuple[str, int, List[str]]]:
        """
        Identify strengths mentioned multiple times.

        Args:
            signals: List of detected signals
            min_mentions: Minimum mentions to be considered a strength

        Returns:
            List of (strength_type, count, sample_excerpts)
        """
        # Focus on positive signals
        positive_signals = [
            s for s in signals
            if s.signal_type in ["loyalty", "repeat", "social_mention"] or s.review_rating >= 4
        ]

        # Group by signal type
        grouped = defaultdict(list)
        for signal in positive_signals:
            grouped[signal.signal_type].append(signal)

        # Filter by minimum mentions
        strengths = []
        for signal_type, signal_list in grouped.items():
            if len(signal_list) >= min_mentions:
                excerpts = [s.excerpt for s in signal_list[:5]]  # Max 5 samples
                strengths.append((signal_type, len(signal_list), excerpts))

        # Sort by frequency
        strengths.sort(key=lambda x: x[1], reverse=True)

        return strengths


# Example usage
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()

    # Create sample reviews
    sample_reviews = [
        Review(
            cafe_name="Test Cafe",
            rating=5,
            text="This is my spot! The barista knows my order and I come here every morning.",
            date=datetime.now(),
            reviewer_name="John"
        ),
        Review(
            cafe_name="Test Cafe",
            rating=2,
            text="Used to be great, but quality went downhill. Not worth it anymore.",
            date=datetime.now(),
            reviewer_name="Jane"
        ),
        Review(
            cafe_name="Test Cafe",
            rating=5,
            text="First time visiting and it was confusing to order, but the space is Instagram-worthy!",
            date=datetime.now(),
            reviewer_name="Bob"
        ),
    ]

    batch = ReviewBatch(
        cafe_name="Test Cafe",
        location="Toronto",
        reviews=sample_reviews,
        total_reviews=len(sample_reviews),
        average_rating=4.0,
        date_range_start=datetime.now(),
        date_range_end=datetime.now()
    )

    # Analyze
    analyzer = SentimentAnalyzer()
    signals = analyzer.analyze_review_batch(batch)

    console.print(f"\n[bold]Detected {len(signals)} signals:[/bold]\n")

    for signal in signals:
        console.print(f"[cyan]{signal.signal_type}[/cyan]: {signal.keywords}")
        console.print(f"  Excerpt: {signal.excerpt}\n")

    # Get summaries
    summaries = analyzer.summarize_signals(signals)

    console.print(f"\n[bold]Signal summaries:[/bold]\n")
    for summary in summaries:
        console.print(f"[yellow]{summary.signal_type}[/yellow]: {summary.count} mentions")
        console.print(f"  Keywords: {', '.join(summary.keywords_found)}\n")
