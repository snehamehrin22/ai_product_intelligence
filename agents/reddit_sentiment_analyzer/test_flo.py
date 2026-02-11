"""
Quick test for Flo Health analysis
"""

import asyncio
from modules.brand_selector import BrandSelector
from modules.google_search import GoogleSearcher
from modules.reddit_scraper import RedditScraper
from modules.data_processor import DataProcessor
from modules.analysis import Analyzer

async def test_flo_health():
    brand_name = "Flo Health"

    print(f"\n🔍 Starting analysis for: {brand_name}\n")

    # Step 1: Create/get prospect
    print("Step 1: Getting prospect...")
    selector = BrandSelector()
    prospect = await selector.get_or_create_prospect(brand_name)
    print(f"✅ Prospect ID: {prospect['id']}\n")

    # Step 2: Search Reddit URLs
    print("Step 2: Searching Reddit URLs...")
    searcher = GoogleSearcher()
    reddit_urls = await searcher.search_reddit_urls(brand_name, "")
    print(f"✅ Found {len(reddit_urls)} URLs\n")

    await searcher.update_prospect_urls(prospect['id'], reddit_urls, brand_name)

    # Step 3: Scrape Reddit
    print("Step 3: Scraping Reddit posts...")
    scraper = RedditScraper()
    posts_comments = await scraper.scrape_all_urls(reddit_urls, brand_name, prospect['id'])
    print(f"✅ Scraped {len(posts_comments)} posts/comments\n")

    # Step 4: Process data
    print("Step 4: Processing data...")
    processor = DataProcessor()
    cleaned_data = await processor.process_data(posts_comments, brand_name, prospect['id'])
    print(f"✅ Cleaned {len(cleaned_data)} items\n")

    # Step 5: Analyze
    print("Step 5: Running AI analysis...")
    analyzer = Analyzer()
    result = await analyzer.analyze(cleaned_data, brand_name, prospect['id'])
    print(f"✅ Analysis complete!\n")

    print("="*70)
    print("KEY INSIGHT:")
    print("="*70)
    print(result['key_insight'])
    print("\n")

    print("="*70)
    print("HTML saved to database")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_flo_health())
