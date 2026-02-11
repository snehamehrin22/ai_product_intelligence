"""
Brand Reddit Analysis - Main Workflow
Orchestrates the complete brand analysis pipeline
"""

import asyncio
from rich.console import Console
from rich.prompt import Prompt, Confirm
from modules.brand_selector import BrandSelector
from modules.google_search import GoogleSearcher
from modules.reddit_scraper import RedditScraper
from modules.data_processor import DataProcessor
from modules.analysis import Analyzer
from utils.logger import setup_logger

console = Console()
logger = setup_logger()


async def main():
    """Main workflow orchestrator"""
    console.print("\n[bold cyan]🔍 Brand Reddit Analysis Tool[/bold cyan]\n")

    # Step 1: Brand Selection
    console.print("[yellow]Step 1: Brand Selection[/yellow]")
    brand_selector = BrandSelector()

    # Give user 3 options
    console.print("\n[cyan]Choose an option:[/cyan]")
    console.print("1. Run analysis for ALL prospects")
    console.print("2. Select ONE prospect from database")
    console.print("3. Input a NEW brand name")

    choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3"], default="2")

    if choice == "1":
        # Run all prospects
        prospects = await brand_selector.get_all_prospects()
        console.print(f"[green]Found {len(prospects)} prospects to analyze[/green]")

    elif choice == "2":
        # Select from existing prospects
        all_prospects = await brand_selector.get_all_prospects()

        if not all_prospects:
            console.print("[red]No prospects found in database. Please create one first.[/red]")
            brand_name = Prompt.ask("Enter brand name to create")
            prospect = await brand_selector.get_or_create_prospect(brand_name)
            prospects = [prospect]
        else:
            console.print(f"\n[green]Found {len(all_prospects)} prospects[/green]")

            # Show numbered list
            for i, p in enumerate(all_prospects, 1):
                console.print(f"{i}. {p['brand_name']} ({p.get('industry_category', 'N/A')})")

            # Let user select by number
            selection = Prompt.ask(
                "\nEnter the number of the prospect to analyze",
                choices=[str(i) for i in range(1, len(all_prospects) + 1)]
            )

            selected_prospect = all_prospects[int(selection) - 1]
            console.print(f"[green]✓ Selected: {selected_prospect['brand_name']}[/green]")
            prospects = [selected_prospect]

    else:
        # Input new brand name
        brand_name = Prompt.ask("Enter brand name to analyze")
        prospect = await brand_selector.get_or_create_prospect(brand_name)
        prospects = [prospect]

    # Process each prospect
    for prospect in prospects:
        await process_prospect(prospect)


async def process_prospect(prospect: dict):
    """Process a single prospect through the entire pipeline"""
    brand_name = prospect['brand_name']
    prospect_id = prospect['id']
    
    console.print(f"\n[bold blue]Processing: {brand_name}[/bold blue]")
    
    try:
        # Step 2: Google Search for Reddit URLs
        console.print(f"[yellow]Step 2: Searching Reddit URLs for {brand_name}[/yellow]")
        searcher = GoogleSearcher()
        reddit_urls = await searcher.search_reddit_urls(brand_name, prospect.get('industry_category', ''))
        
        if not reddit_urls:
            console.print(f"[red]No Reddit URLs found for {brand_name}[/red]")
            return
        
        console.print(f"[green]Found {len(reddit_urls)} Reddit URLs[/green]")
        
        # Step 3: Update prospect with URLs
        await searcher.update_prospect_urls(prospect_id, reddit_urls, brand_name)
        
        # Step 4: Scrape Reddit Posts & Comments
        console.print(f"[yellow]Step 3: Scraping Reddit posts & comments[/yellow]")
        scraper = RedditScraper()
        posts_comments = await scraper.scrape_all_urls(reddit_urls, brand_name, prospect_id)
        
        console.print(f"[green]Scraped {len(posts_comments)} posts/comments[/green]")
        
        # Step 5: Process & Clean Data
        console.print(f"[yellow]Step 4: Processing and cleaning data[/yellow]")
        processor = DataProcessor()
        cleaned_data = await processor.process_data(posts_comments, brand_name, prospect_id)
        
        console.print(f"[green]Cleaned data: {len(cleaned_data)} valid items[/green]")
        
        # Step 6: Run Analysis
        console.print(f"[yellow]Step 5: Running ChatGPT analysis[/yellow]")
        analyzer = Analyzer()
        analysis_result = await analyzer.analyze(cleaned_data, brand_name, prospect_id)
        
        console.print(f"[bold green]✓ Analysis complete for {brand_name}![/bold green]")
        console.print(f"[cyan]Key Insight:[/cyan] {analysis_result['key_insight'][:200]}...")
        
    except Exception as e:
        logger.error(f"Error processing {brand_name}: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    asyncio.run(main())

