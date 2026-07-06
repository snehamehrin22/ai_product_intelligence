#!/usr/bin/env python3
"""
Run comprehensive research analysis on cafe reviews.

Uses the 13-section qualitative research framework.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cafe_intelligence.apify_scraper import ApifyScraper

console = Console()


def load_research_prompt() -> str:
    """Load the research analysis prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "research_analysis.txt"
    return prompt_path.read_text(encoding="utf-8")


def format_reviews_for_analysis(batch) -> str:
    """Format reviews into a text block for analysis."""
    lines = [
        f"CAFE: {batch.cafe_name}",
        f"LOCATION: {batch.location}",
        f"TOTAL REVIEWS: {batch.total_reviews}",
        f"AVERAGE RATING: {batch.average_rating:.2f}/5.0",
        f"DATE RANGE: {batch.date_range_start.date()} to {batch.date_range_end.date()}",
        "",
        "=" * 80,
        "REVIEWS",
        "=" * 80,
        ""
    ]

    for i, review in enumerate(batch.reviews, 1):
        lines.append(f"--- Review {i} ---")
        lines.append(f"Rating: {review.rating}/5")
        lines.append(f"Date: {review.date.date()}")
        if review.reviewer_name:
            lines.append(f"Reviewer: {review.reviewer_name}")
        lines.append(f"\n{review.text}\n")

    return "\n".join(lines)


def run_research_analysis(reviews_text: str, cafe_name: str) -> str:
    """Run the research analysis using OpenAI."""

    # Load prompt
    system_prompt = load_research_prompt()

    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    console.print("[yellow]Sending to OpenAI for analysis...[/yellow]")
    console.print(f"[dim]Model: gpt-4o[/dim]")
    console.print(f"[dim]Input tokens: ~{len(reviews_text.split())}[/dim]\n")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": reviews_text}
        ],
        temperature=0.3,
        max_tokens=16000  # Long output expected for 13 sections
    )

    return response.choices[0].message.content


def save_analysis(cafe_name: str, analysis: str) -> Path:
    """Save analysis to markdown file."""
    # Create analysis directory
    output_dir = Path(__file__).parent.parent / "analysis"
    output_dir.mkdir(exist_ok=True)

    # Sanitize cafe name
    safe_name = cafe_name.lower().replace(" ", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_research_{timestamp}.md"
    filepath = output_dir / filename

    # Add header
    content = f"# Research Analysis: {cafe_name}\n\n"
    content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += "---\n\n"
    content += analysis

    filepath.write_text(content, encoding="utf-8")

    return filepath


def main():
    """Run complete research analysis workflow."""

    # Load environment variables
    load_dotenv()

    console.print("\n[bold cyan]🔬 Cafe Research Analysis[/bold cyan]\n")
    console.print("[dim]13-Section Qualitative Research Framework[/dim]\n")

    # Get cafe name from command line or prompt
    if len(sys.argv) >= 2:
        cafe_name = sys.argv[1]
        location = sys.argv[2] if len(sys.argv) >= 3 else "Toronto"
    else:
        cafe_name = console.input("[yellow]Enter cafe name:[/yellow] ")
        location = console.input("[yellow]Enter location (default: Toronto):[/yellow] ") or "Toronto"

    max_reviews = int(os.getenv("MAX_REVIEWS_PER_CAFE", "100"))

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
        # Step 2: Format reviews for analysis
        # ====================================================================

        console.print("[bold cyan]Step 2:[/bold cyan] Formatting reviews for analysis...")

        reviews_text = format_reviews_for_analysis(batch)
        console.print(f"[green]✓ Formatted {len(batch.reviews)} reviews[/green]\n")

        # ====================================================================
        # Step 3: Run research analysis
        # ====================================================================

        console.print("[bold cyan]Step 3:[/bold cyan] Running comprehensive research analysis...")
        console.print("[dim]This may take 2-3 minutes for deep analysis...[/dim]\n")

        analysis = run_research_analysis(reviews_text, cafe_name)

        console.print(f"[green]✓ Analysis complete[/green]\n")

        # ====================================================================
        # Step 4: Save and display
        # ====================================================================

        console.print("[bold cyan]Step 4:[/bold cyan] Saving analysis...")

        saved_path = save_analysis(cafe_name, analysis)

        console.print(f"[green]✓ Saved to: {saved_path}[/green]\n")

        # ====================================================================
        # Display the analysis
        # ====================================================================

        console.print("=" * 80)
        console.print(Markdown(analysis))
        console.print("=" * 80)

        console.print(f"\n[bold green]✅ Research analysis complete![/bold green]")
        console.print(f"\n[dim]Cafe: {cafe_name}")
        console.print(f"Reviews analyzed: {batch.total_reviews}")
        console.print(f"Output saved: {saved_path}[/dim]\n")

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
