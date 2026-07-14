"""
Insight generator - maps behavioral signals to 5-layer framework.

Uses OpenAI to generate actionable experiments from review patterns.
"""

import os
import json
from pathlib import Path
from typing import List
from openai import OpenAI
from rich.console import Console

from .schemas import (
    ReviewBatch, RetentionSignal, SignalSummary,
    BehavioralInsight, FrameworkAnalysis
)

console = Console()


class InsightGenerator:
    """Generates actionable insights from behavioral signals."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize insight generator with OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

        # Load system prompt
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "insight_generator.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def generate_insights(
        self,
        batch: ReviewBatch,
        signals: List[RetentionSignal],
        signal_summaries: List[SignalSummary]
    ) -> FrameworkAnalysis:
        """
        Generate behavioral insights from review signals.

        Args:
            batch: ReviewBatch with all reviews
            signals: List of detected RetentionSignals
            signal_summaries: Aggregated signal summaries

        Returns:
            FrameworkAnalysis with insights mapped to 5 layers
        """
        console.print(f"\n[cyan]Generating insights for {batch.cafe_name}...[/cyan]")

        # Prepare input for LLM
        user_prompt = self._create_user_prompt(batch, signal_summaries)

        # Call OpenAI with JSON mode
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            # Parse response
            response_text = response.choices[0].message.content
            data = json.loads(response_text)

            # Validate and create BehavioralInsight objects
            insights = []

            for insight_data in data.get("insights", []):
                try:
                    insight = BehavioralInsight(**insight_data)
                    insights.append(insight)
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to parse insight: {e}[/yellow]")
                    continue

            if not insights:
                console.print("[yellow]Warning: No valid insights generated[/yellow]")
                # Return empty analysis
                return self._create_empty_analysis(batch)

            # Group insights by framework layer
            analysis = self._group_insights_by_layer(batch, insights)

            console.print(f"[green]✓ Generated {len(insights)} insights across {len(analysis.top_3_findings)} priority areas[/green]")

            return analysis

        except Exception as e:
            console.print(f"[red]Error generating insights: {e}[/red]")
            return self._create_empty_analysis(batch)

    def _create_user_prompt(
        self,
        batch: ReviewBatch,
        signal_summaries: List[SignalSummary]
    ) -> str:
        """
        Create user prompt with cafe data and signals.

        Args:
            batch: ReviewBatch
            signal_summaries: Signal summaries

        Returns:
            Formatted prompt string
        """
        # Build signal summary text
        signal_text = []

        for summary in signal_summaries:
            signal_text.append(f"\n**{summary.signal_type}** ({summary.count} mentions)")
            signal_text.append(f"Keywords: {', '.join(summary.keywords_found)}")
            signal_text.append("Sample excerpts:")
            for i, excerpt in enumerate(summary.sample_excerpts[:3], 1):
                signal_text.append(f"  {i}. \"{excerpt}\"")

        signals_str = "\n".join(signal_text)

        prompt = f"""
# Cafe Information

**Name:** {batch.cafe_name}
**Location:** {batch.location}
**Total Reviews Analyzed:** {batch.total_reviews}
**Average Rating:** {batch.average_rating:.1f}/5.0
**Date Range:** {batch.date_range_start.date()} to {batch.date_range_end.date()}

# Detected Behavioral Signals

{signals_str}

# Task

Analyze these signals and generate actionable insights mapped to the 5-layer framework (onboarding, activation, retention, monetization, social).

For each significant pattern (minimum 3 mentions), create an insight with:
- Framework layer it maps to
- Clear finding (what you observed)
- Sentiment (positive/negative/mixed)
- Evidence count and sample reviews
- Specific experiment to run
- Expected impact

Return insights as a JSON object with an "insights" array.
"""

        return prompt

    def _group_insights_by_layer(
        self,
        batch: ReviewBatch,
        insights: List[BehavioralInsight]
    ) -> FrameworkAnalysis:
        """
        Group insights by framework layer and select top 3.

        Args:
            batch: ReviewBatch
            insights: List of all insights

        Returns:
            FrameworkAnalysis with insights grouped by layer
        """
        # Group by layer
        by_layer = {
            "onboarding": [],
            "activation": [],
            "retention": [],
            "monetization": [],
            "social": []
        }

        for insight in insights:
            by_layer[insight.framework_layer].append(insight)

        # Select top 3 overall (by evidence count + confidence)
        def priority_score(insight: BehavioralInsight) -> int:
            confidence_scores = {"high": 3, "medium": 2, "low": 1}
            return insight.evidence_count * confidence_scores[insight.confidence]

        sorted_insights = sorted(insights, key=priority_score, reverse=True)
        top_3 = sorted_insights[:3]

        # Create analysis
        analysis = FrameworkAnalysis(
            cafe_name=batch.cafe_name,
            onboarding_insights=by_layer["onboarding"],
            activation_insights=by_layer["activation"],
            retention_insights=by_layer["retention"],
            monetization_insights=by_layer["monetization"],
            social_insights=by_layer["social"],
            top_3_findings=top_3,
            total_reviews_analyzed=batch.total_reviews,
            date_range=f"{batch.date_range_start.date()} to {batch.date_range_end.date()}"
        )

        return analysis

    def _create_empty_analysis(self, batch: ReviewBatch) -> FrameworkAnalysis:
        """Create empty analysis when generation fails."""

        # Create a placeholder insight
        placeholder = BehavioralInsight(
            framework_layer="retention",
            finding="No significant patterns detected in current review sample",
            sentiment="mixed",
            evidence_count=0,
            confidence="low",
            sample_reviews=["Not enough data"],
            recommended_experiment="Collect more reviews and re-analyze",
            expected_impact="Need more data for actionable insights",
            cafe_name=batch.cafe_name
        )

        return FrameworkAnalysis(
            cafe_name=batch.cafe_name,
            top_3_findings=[placeholder],
            total_reviews_analyzed=batch.total_reviews,
            date_range=f"{batch.date_range_start.date()} to {batch.date_range_end.date()}"
        )


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    from datetime import datetime

    load_dotenv()

    # Create sample data
    from .sentiment_analyzer import SentimentAnalyzer
    from .schemas import Review

    sample_reviews = [
        Review(
            cafe_name="Test Cafe",
            rating=5,
            text="This is my regular spot! The barista Sarah knows my name and order. I come every morning before work.",
            date=datetime.now(),
            reviewer_name="John"
        ),
        Review(
            cafe_name="Test Cafe",
            rating=2,
            text="Used to love this place but quality went downhill. Coffee tastes burnt now and service is inconsistent.",
            date=datetime.now(),
            reviewer_name="Jane"
        ),
        Review(
            cafe_name="Test Cafe",
            rating=4,
            text="First time here - menu was a bit confusing but the space is absolutely Instagram-worthy! Will come back.",
            date=datetime.now(),
            reviewer_name="Bob"
        ),
    ]

    batch = ReviewBatch(
        cafe_name="Test Cafe",
        location="Toronto",
        reviews=sample_reviews,
        total_reviews=len(sample_reviews),
        average_rating=3.7,
        date_range_start=datetime.now(),
        date_range_end=datetime.now()
    )

    # Analyze
    analyzer = SentimentAnalyzer()
    signals = analyzer.analyze_review_batch(batch)
    summaries = analyzer.summarize_signals(signals)

    # Generate insights
    generator = InsightGenerator()
    analysis = generator.generate_insights(batch, signals, summaries)

    console.print(f"\n[bold]Top 3 Findings:[/bold]\n")
    for i, finding in enumerate(analysis.top_3_findings, 1):
        console.print(f"[yellow]{i}. {finding.framework_layer.upper()}[/yellow]")
        console.print(f"   Finding: {finding.finding}")
        console.print(f"   Experiment: {finding.recommended_experiment}\n")
