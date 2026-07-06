#!/usr/bin/env python3
"""
Run complete cafe intelligence analysis for a single cafe.

This is the main entry point for analyzing one cafe.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cafe_intelligence.apify_scraper import ApifyScraper
from cafe_intelligence.sentiment_analyzer import SentimentAnalyzer
from cafe_intelligence.insight_generator import InsightGenerator
from cafe_intelligence.json_logger import JSONLogger

console = Console()


def main():
    """Run complete analysis workflow."""

    # Load environment variables
    load_dotenv()

    console.print("\n[bold cyan]🔍 Cafe Review Intelligence Agent[/bold cyan]\n")

    # Get cafe name from command line or prompt
    if len(sys.argv) >= 2:
        cafe_name = sys.argv[1]
        location = sys.argv[2] if len(sys.argv) >= 3 else "Toronto"
    else:
        cafe_name = console.input("[yellow]Enter cafe name:[/yellow] ")
        location = console.input("[yellow]Enter location (default: Toronto):[/yellow] ") or "Toronto"

    max_reviews = int(os.getenv("MAX_REVIEWS_PER_CAFE", "50"))

    console.print(f"\n[bold]Analyzing:[/bold] {cafe_name} ({location})")
    console.print(f"[dim]Max reviews: {max_reviews}[/dim]\n")

    try:
        # ====================================================================
        # Step 1: Scrape reviews from Google Maps
        # ====================================================================

        console.print("[bold cyan]Step 1:[/bold cyan] Scraping reviews from Google Maps...")

        scraper = ApifyScraper()
        batch = scraper.scrape_cafe_reviews(
            cafe_name=cafe_name,
            location=location,
            max_reviews=max_reviews
        )

        if not batch.reviews:
            console.print("[red]No reviews found. Exiting.[/red]")
            return

        console.print(f"[green]✓ Found {batch.total_reviews} reviews[/green]")
        console.print(f"[dim]Average rating: {batch.average_rating:.1f}/5.0[/dim]")
        console.print(f"[dim]Date range: {batch.date_range_start.date()} to {batch.date_range_end.date()}[/dim]\n")

        # ====================================================================
        # Step 2: Detect behavioral signals
        # ====================================================================

        console.print("[bold cyan]Step 2:[/bold cyan] Detecting behavioral signals...")

        analyzer = SentimentAnalyzer()
        signals = analyzer.analyze_review_batch(batch)
        signal_summaries = analyzer.summarize_signals(signals)

        console.print(f"[green]✓ Detected {len(signals)} behavioral signals[/green]")

        # Display signal summary
        if signal_summaries:
            table = Table(title="Detected Signals", show_header=True)
            table.add_column("Signal Type", style="cyan")
            table.add_column("Count", style="yellow")
            table.add_column("Sample Keywords", style="dim")

            for summary in signal_summaries[:10]:  # Top 10
                keywords = ", ".join(summary.keywords_found[:3])  # First 3 keywords
                table.add_row(summary.signal_type, str(summary.count), keywords)

            console.print(table)
            console.print()

        # ====================================================================
        # Step 3: Generate insights mapped to framework
        # ====================================================================

        console.print("[bold cyan]Step 3:[/bold cyan] Generating actionable insights...")

        generator = InsightGenerator()
        analysis = generator.generate_insights(batch, signals, signal_summaries)

        # ====================================================================
        # Step 4: Display results
        # ====================================================================

        console.print(f"\n[bold green]✓ Analysis complete for {cafe_name}[/bold green]\n")

        # Display top 3 findings
        console.print("[bold yellow]🎯 Top 3 Priority Findings:[/bold yellow]\n")

        for i, finding in enumerate(analysis.top_3_findings, 1):
            panel_content = f"""**Layer:** {finding.framework_layer.upper()}

**Finding:** {finding.finding}

**Sentiment:** {finding.sentiment} | **Evidence:** {finding.evidence_count} mentions | **Confidence:** {finding.confidence}

**Recommended Experiment:**
{finding.recommended_experiment}

**Expected Impact:**
{finding.expected_impact}
"""
            console.print(Panel(
                Markdown(panel_content),
                title=f"Finding #{i}",
                border_style="yellow" if i == 1 else "cyan"
            ))
            console.print()

        # Display insights by layer
        console.print("[bold]📊 Insights by Framework Layer:[/bold]\n")

        layers = [
            ("Onboarding", analysis.onboarding_insights),
            ("Activation", analysis.activation_insights),
            ("Retention", analysis.retention_insights),
            ("Monetization", analysis.monetization_insights),
            ("Social", analysis.social_insights),
        ]

        for layer_name, insights in layers:
            if insights:
                console.print(f"[cyan]• {layer_name}:[/cyan] {len(insights)} insight(s)")

        console.print()

        # ====================================================================
        # Step 5: Save to JSON files
        # ====================================================================

        console.print("[bold cyan]Step 4:[/bold cyan] Saving results to JSON files...")

        logger = JSONLogger()
        saved_paths = logger.save_complete_run(batch, signals, analysis)

        # ====================================================================
        # Done!
        # ====================================================================

        console.print("[bold green]✅ Analysis complete![/bold green]")
        console.print(f"\n[dim]Cafe: {cafe_name}")
        console.print(f"Reviews analyzed: {batch.total_reviews}")
        console.print(f"Signals detected: {len(signals)}")
        console.print(f"Insights generated: {len(analysis.top_3_findings)}")
        console.print(f"\nResults saved in: {logger.output_dir}/[/dim]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(1)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
