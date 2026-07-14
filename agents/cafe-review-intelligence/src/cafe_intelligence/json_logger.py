"""
JSON logger for storing cafe intelligence results.

Saves reviews, signals, and insights as JSON files in data/ directory.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List
from rich.console import Console

from .schemas import (
    Review, ReviewBatch, RetentionSignal,
    BehavioralInsight, FrameworkAnalysis
)

console = Console()


class JSONLogger:
    """Saves analysis results as structured JSON files."""

    def __init__(self, output_dir: str = None):
        """
        Initialize JSON logger.

        Args:
            output_dir: Directory to save JSON files (defaults to ./data)
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to data/ in project root
            self.output_dir = Path(__file__).parent.parent.parent / "data"

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_review_batch(self, batch: ReviewBatch) -> Path:
        """
        Save review batch to JSON file.

        Args:
            batch: ReviewBatch to save

        Returns:
            Path to saved file
        """
        # Create filename with cafe name and timestamp
        safe_name = self._sanitize_filename(batch.cafe_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_reviews_{timestamp}.json"
        filepath = self.output_dir / filename

        # Convert to dict (Pydantic models have .model_dump())
        data = {
            "cafe_name": batch.cafe_name,
            "location": batch.location,
            "total_reviews": batch.total_reviews,
            "average_rating": batch.average_rating,
            "date_range_start": batch.date_range_start.isoformat(),
            "date_range_end": batch.date_range_end.isoformat(),
            "scraped_at": datetime.now().isoformat(),
            "reviews": [
                {
                    "rating": r.rating,
                    "text": r.text,
                    "date": r.date.isoformat(),
                    "reviewer_name": r.reviewer_name,
                    "source": r.source
                }
                for r in batch.reviews
            ]
        }

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ Saved reviews to: {filepath.name}[/green]")
        return filepath

    def save_signals(
        self,
        cafe_name: str,
        signals: List[RetentionSignal]
    ) -> Path:
        """
        Save retention signals to JSON file.

        Args:
            cafe_name: Name of cafe
            signals: List of RetentionSignals

        Returns:
            Path to saved file
        """
        safe_name = self._sanitize_filename(cafe_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_signals_{timestamp}.json"
        filepath = self.output_dir / filename

        # Group signals by type
        by_type = {}
        for signal in signals:
            if signal.signal_type not in by_type:
                by_type[signal.signal_type] = []

            by_type[signal.signal_type].append({
                "keywords": signal.keywords,
                "excerpt": signal.excerpt,
                "review_rating": signal.review_rating,
                "review_date": signal.review_date.isoformat()
            })

        data = {
            "cafe_name": cafe_name,
            "total_signals": len(signals),
            "detected_at": datetime.now().isoformat(),
            "signals_by_type": {
                signal_type: {
                    "count": len(signal_list),
                    "signals": signal_list
                }
                for signal_type, signal_list in by_type.items()
            }
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ Saved signals to: {filepath.name}[/green]")
        return filepath

    def save_analysis(self, analysis: FrameworkAnalysis) -> Path:
        """
        Save framework analysis to JSON file.

        Args:
            analysis: FrameworkAnalysis to save

        Returns:
            Path to saved file
        """
        safe_name = self._sanitize_filename(analysis.cafe_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_analysis_{timestamp}.json"
        filepath = self.output_dir / filename

        # Convert insights to dicts
        def insight_to_dict(insight: BehavioralInsight) -> dict:
            return {
                "framework_layer": insight.framework_layer,
                "finding": insight.finding,
                "sentiment": insight.sentiment,
                "evidence_count": insight.evidence_count,
                "confidence": insight.confidence,
                "sample_reviews": insight.sample_reviews,
                "recommended_experiment": insight.recommended_experiment,
                "expected_impact": insight.expected_impact
            }

        data = {
            "cafe_name": analysis.cafe_name,
            "total_reviews_analyzed": analysis.total_reviews_analyzed,
            "date_range": analysis.date_range,
            "generated_at": analysis.generated_at.isoformat(),

            "top_3_findings": [
                insight_to_dict(i) for i in analysis.top_3_findings
            ],

            "insights_by_layer": {
                "onboarding": [insight_to_dict(i) for i in analysis.onboarding_insights],
                "activation": [insight_to_dict(i) for i in analysis.activation_insights],
                "retention": [insight_to_dict(i) for i in analysis.retention_insights],
                "monetization": [insight_to_dict(i) for i in analysis.monetization_insights],
                "social": [insight_to_dict(i) for i in analysis.social_insights],
            },

            "summary": {
                "total_insights": len(analysis.top_3_findings),
                "insights_per_layer": {
                    "onboarding": len(analysis.onboarding_insights),
                    "activation": len(analysis.activation_insights),
                    "retention": len(analysis.retention_insights),
                    "monetization": len(analysis.monetization_insights),
                    "social": len(analysis.social_insights),
                }
            }
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ Saved analysis to: {filepath.name}[/green]")
        return filepath

    def save_complete_run(
        self,
        batch: ReviewBatch,
        signals: List[RetentionSignal],
        analysis: FrameworkAnalysis
    ) -> dict:
        """
        Save all data from a complete analysis run.

        Args:
            batch: ReviewBatch
            signals: List of RetentionSignals
            analysis: FrameworkAnalysis

        Returns:
            Dict with paths to all saved files
        """
        console.print("\n[cyan]Saving results to JSON files...[/cyan]")

        paths = {
            "reviews": self.save_review_batch(batch),
            "signals": self.save_signals(batch.cafe_name, signals),
            "analysis": self.save_analysis(analysis)
        }

        console.print(f"[green bold]✓ All results saved to: {self.output_dir}/[/green bold]\n")

        return paths

    def get_analysis_files(self, cafe_name: str = None) -> List[Path]:
        """
        Get list of analysis files, optionally filtered by cafe name.

        Args:
            cafe_name: Optional cafe name to filter by

        Returns:
            List of Path objects
        """
        pattern = "*_analysis_*.json"

        if cafe_name:
            safe_name = self._sanitize_filename(cafe_name)
            pattern = f"{safe_name}_analysis_*.json"

        return sorted(self.output_dir.glob(pattern), reverse=True)

    def load_latest_analysis(self, cafe_name: str) -> dict:
        """
        Load the most recent analysis for a cafe.

        Args:
            cafe_name: Name of cafe

        Returns:
            Dict with analysis data, or None if not found
        """
        files = self.get_analysis_files(cafe_name)

        if not files:
            return None

        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def _sanitize_filename(self, name: str) -> str:
        """
        Convert cafe name to safe filename.

        Args:
            name: Cafe name

        Returns:
            Sanitized filename
        """
        # Remove special characters, replace spaces with underscores, lowercase
        safe = name.lower()
        safe = safe.replace(" ", "_")
        safe = "".join(c for c in safe if c.isalnum() or c == "_")
        return safe


# Example usage
if __name__ == "__main__":
    from datetime import datetime

    logger = JSONLogger()

    # Create sample data
    from .schemas import Review

    sample_reviews = [
        Review(
            cafe_name="Test Cafe",
            rating=5,
            text="This is my regular spot! Love it here.",
            date=datetime.now(),
            reviewer_name="John"
        ),
    ]

    batch = ReviewBatch(
        cafe_name="Test Cafe",
        location="Toronto",
        reviews=sample_reviews,
        total_reviews=1,
        average_rating=5.0,
        date_range_start=datetime.now(),
        date_range_end=datetime.now()
    )

    # Save
    logger.save_review_batch(batch)

    console.print(f"\n[bold]Output directory:[/bold] {logger.output_dir}")
    console.print(f"\n[bold]Files saved:[/bold]")
    for file in logger.output_dir.glob("*.json"):
        console.print(f"  - {file.name}")
