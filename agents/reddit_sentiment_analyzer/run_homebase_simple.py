"""
Simple script to fetch Reddit comments for Homebase without database storage
"""

import asyncio
import httpx
import json
from rich.console import Console
from rich.table import Table

console = Console()
APIFY_API_KEY = "apify_api_eQcKRrWedad7VWNUiWdY5nELkJij022Hkr3E"


async def search_reddit_urls(brand_name: str) -> list:
    """Search Google for Reddit URLs about the brand"""
    search_query = f"reddit:{brand_name}"
    console.print(f"[yellow]Searching Google for: {search_query}[/yellow]")

    # Call Apify Google Search
    url = f"https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items"
    params = {"token": APIFY_API_KEY}
    headers = {"Content-Type": "application/json"}
    payload = {"queries": search_query, "maxPagesPerQuery": 1}

    async with httpx.AsyncClient(timeout=310.0) as client:
        response = await client.post(url, json=payload, headers=headers, params=params)
        response.raise_for_status()
        results = response.json()

    # Extract Reddit URLs
    reddit_urls = []
    seen_urls = set()
    for result in results:
        organic_results = result.get('organicResults', [])
        for item in organic_results:
            url = item.get('url', '')
            if 'reddit.com/r/' in url and url not in seen_urls:
                reddit_urls.append(url)
                seen_urls.add(url)

    # Get all URLs (no limit)
    console.print(f"[green]Found {len(reddit_urls)} Reddit URLs[/green]")
    return reddit_urls


async def scrape_reddit_url(url: str) -> list:
    """Scrape posts and comments from a Reddit URL"""
    console.print(f"[cyan]Scraping: {url}[/cyan]")

    api_url = f"https://api.apify.com/v2/acts/trudax~reddit-scraper-lite/run-sync-get-dataset-items"
    params = {"token": APIFY_API_KEY}
    headers = {"Content-Type": "application/json"}
    payload = {
        "startUrls": [{"url": url}],
        "maxPosts": 999999,
        "maxComments": 999999,
        "maxCommunitiesCount": 1,
        "scrollTimeout": 40,
        "proxy": {"useApifyProxy": True}
    }

    async with httpx.AsyncClient(timeout=310.0) as client:
        response = await client.post(api_url, json=payload, headers=headers, params=params)
        response.raise_for_status()
        results = response.json()

    return results


async def main():
    """Main function to fetch Homebase Reddit data"""
    brand_name = "Homebase"

    console.print(f"\n[bold cyan]Fetching Reddit data for: {brand_name}[/bold cyan]\n")

    # Step 1: Search for Reddit URLs
    try:
        reddit_urls = await search_reddit_urls(brand_name)

        if not reddit_urls:
            console.print("[red]No Reddit URLs found![/red]")
            return

        # Display found URLs
        console.print("\n[bold]Found Reddit URLs:[/bold]")
        for i, url in enumerate(reddit_urls, 1):
            console.print(f"{i}. {url}")

        # Step 2: Scrape each URL
        all_comments = []
        all_posts = []

        for url in reddit_urls:
            try:
                data = await scrape_reddit_url(url)

                for item in data:
                    data_type = item.get('dataType', 'post')
                    if data_type == 'comment':
                        all_comments.append({
                            'url': url,
                            'body': item.get('body', ''),
                            'upvotes': item.get('upVotes', 0),
                            'created': item.get('createdAt', ''),
                            'community': item.get('communityName', '')
                        })
                    else:
                        all_posts.append({
                            'url': url,
                            'title': item.get('title', ''),
                            'body': item.get('body', ''),
                            'upvotes': item.get('upVotes', 0),
                            'created': item.get('createdAt', ''),
                            'community': item.get('communityName', '')
                        })

                console.print(f"[green]✓ Scraped {len(data)} items from this URL[/green]")

            except Exception as e:
                console.print(f"[red]Error scraping {url}: {str(e)}[/red]")
                continue

        # Display results
        console.print(f"\n[bold green]Total Results:[/bold green]")
        console.print(f"Posts: {len(all_posts)}")
        console.print(f"Comments: {len(all_comments)}")

        # Show sample comments
        console.print("\n[bold cyan]Sample Comments:[/bold cyan]")
        for i, comment in enumerate(all_comments[:10], 1):
            console.print(f"\n{i}. [{comment['community']}] ({comment['upvotes']} upvotes)")
            console.print(f"   {comment['body'][:200]}...")

        # Show sample posts
        console.print("\n[bold cyan]Sample Posts:[/bold cyan]")
        for i, post in enumerate(all_posts[:5], 1):
            console.print(f"\n{i}. [{post['community']}] {post['title']}")
            console.print(f"   Upvotes: {post['upvotes']}")
            if post['body']:
                console.print(f"   {post['body'][:200]}...")

        # Save to JSON file
        output_file = "homebase_reddit_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'brand': brand_name,
                'reddit_urls': reddit_urls,
                'posts': all_posts,
                'comments': all_comments
            }, f, indent=2, ensure_ascii=False)

        console.print(f"\n[bold green]✓ Data saved to: {output_file}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
