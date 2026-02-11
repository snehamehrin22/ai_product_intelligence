"""
Test: Get Reddit posts for Flo Health and store in Supabase
"""

import asyncio
from modules.brand_selector import BrandSelector
from modules.google_search import GoogleSearcher
from modules.reddit_scraper import RedditScraper
from modules.data_processor import DataProcessor

async def test_reddit_scrape():
    brand_name = "Flo Health"

    print(f"\n🔍 Testing Reddit scrape for: {brand_name}\n")

    # Step 1: Create/get prospect
    print("Step 1: Getting prospect...")
    selector = BrandSelector()
    prospect = await selector.get_or_create_prospect(brand_name)
    print(f"✅ Prospect ID: {prospect['id']}")
    print(f"   Brand: {prospect['brand_name']}\n")

    # Step 2: Search Reddit URLs via Google
    print("Step 2: Searching Reddit URLs via Google...")
    searcher = GoogleSearcher()
    reddit_urls = await searcher.search_reddit_urls(brand_name, "")
    print(f"✅ Found {len(reddit_urls)} Reddit URLs")

    for i, url_info in enumerate(reddit_urls[:3], 1):
        print(f"   {i}. {url_info.get('title', 'No title')[:60]}...")
    print()

    # Store URLs in Supabase
    print("Step 3: Storing URLs in Supabase...")
    await searcher.update_prospect_urls(prospect['id'], reddit_urls, brand_name)
    print(f"✅ Stored {len(reddit_urls)} URLs in Supabase\n")

    # Step 4: Scrape Reddit posts/comments
    print("Step 4: Scraping Reddit posts & comments via Apify...")
    scraper = RedditScraper()
    posts_comments = await scraper.scrape_all_urls(reddit_urls, brand_name, prospect['id'])
    print(f"✅ Scraped {len(posts_comments)} posts/comments")
    print(f"   (Stored in Supabase table: brand_reddit_posts_comments)\n")

    # Step 5: Clean the data
    print("Step 5: Processing & cleaning data...")
    processor = DataProcessor()
    cleaned_data = await processor.process_data(posts_comments, brand_name, prospect['id'])
    print(f"✅ Cleaned {len(cleaned_data)} valid items\n")

    # Show sample
    if cleaned_data:
        print("="*70)
        print("SAMPLE POST:")
        print("="*70)
        sample = cleaned_data[0]
        print(f"Subreddit: {sample.get('subreddit')}")
        print(f"Text: {sample.get('text')[:200]}...")
        print(f"Upvotes: {sample.get('upVotes')}")
        print()

    print("="*70)
    print("✅ TEST COMPLETE - Check Supabase for data!")
    print("="*70)
    print(f"Tables to check:")
    print(f"  1. dim_prospects (brand info)")
    print(f"  2. brand_google_reddit (Reddit URLs)")
    print(f"  3. brand_reddit_posts_comments (scraped content)")

if __name__ == "__main__":
    asyncio.run(test_reddit_scrape())
