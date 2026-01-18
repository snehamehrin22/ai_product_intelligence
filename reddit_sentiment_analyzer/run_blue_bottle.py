"""
Quick script to run analysis for Blue Bottle Coffee
"""

import asyncio
from rich.console import Console
from modules.brand_selector import BrandSelector
from modules.google_search import GoogleSearcher
from modules.reddit_scraper import RedditScraper
from modules.data_processor import DataProcessor
from modules.analysis import Analyzer
from utils.logger import setup_logger

console = Console()
logger = setup_logger()

BRAND_NAME = "blue bottle coffee"


async def main():
    """Run analysis for Blue Bottle Coffee"""
    console.print(f"\n[bold cyan]🔍 Running Reddit Analysis for {BRAND_NAME}[/bold cyan]\n")

    # Step 1: Look up existing prospect
    console.print("[yellow]Step 1: Looking up prospect in database[/yellow]")
    brand_selector = BrandSelector()
    prospect = await brand_selector.db.get_prospect_by_name(BRAND_NAME)

    if not prospect:
        console.print(f"[red]✗ Prospect '{BRAND_NAME}' not found in dim_prospects table![/red]")
        console.print(f"[yellow]Please add '{BRAND_NAME}' to dim_prospects first.[/yellow]")
        return

    console.print(f"[green]✓ Found prospect: {prospect['brand_name']}[/green]")
    console.print(f"[green]✓ Prospect ID: {prospect['id']}[/green]")
    console.print(f"[cyan]  Industry: {prospect.get('industry_category', 'N/A')}[/cyan]")
    console.print(f"[cyan]  Location: {prospect.get('hq_location', 'N/A')}[/cyan]")

    # Step 2: Search Reddit URLs
    console.print(f"\n[yellow]Step 2: Searching Reddit URLs for {BRAND_NAME}[/yellow]")
    searcher = GoogleSearcher()
    reddit_urls = await searcher.search_reddit_urls(BRAND_NAME, prospect.get('industry_category', ''))

    if not reddit_urls:
        console.print(f"[red]No Reddit URLs found for {BRAND_NAME}[/red]")
        return

    console.print(f"[green]✓ Found {len(reddit_urls)} Reddit URLs[/green]")

    # Step 3: Save URLs to database
    await searcher.update_prospect_urls(prospect['id'], reddit_urls, BRAND_NAME)
    console.print(f"[green]✓ Saved URLs to database[/green]")

    # Step 4: Scrape Reddit
    console.print(f"\n[yellow]Step 3: Scraping Reddit posts & comments[/yellow]")
    scraper = RedditScraper()
    posts_comments = await scraper.scrape_all_urls(reddit_urls, BRAND_NAME, prospect['id'])

    console.print(f"[green]✓ Scraped {len(posts_comments)} posts/comments[/green]")

    # Step 5: Process & Clean Data
    console.print(f"\n[yellow]Step 4: Processing and cleaning data[/yellow]")
    processor = DataProcessor()
    cleaned_data = await processor.process_data(posts_comments, BRAND_NAME, prospect['id'])

    console.print(f"[green]✓ Cleaned data: {len(cleaned_data)} valid items[/green]")

    # Step 6: Run Analysis
    console.print(f"\n[yellow]Step 5: Running ChatGPT analysis[/yellow]")
    analyzer = Analyzer()
    analysis_result = await analyzer.analyze(cleaned_data, BRAND_NAME, prospect['id'])

    console.print(f"\n[bold green]✓ Analysis complete for {BRAND_NAME}![/bold green]")
    console.print(f"[cyan]Key Insight:[/cyan] {analysis_result['key_insight'][:300]}...")
    console.print(f"\n[green]Full analysis saved to database![/green]")


if __name__ == "__main__":
    asyncio.run(main())
