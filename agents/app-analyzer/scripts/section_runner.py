#!/usr/bin/env python3
"""
Unified Section Runner
Routes analysis sections based on section name, not tool type
"""

import sys
import os
import json
import asyncio
import requests
from pathlib import Path

# Add credentials path
sys.path.append(os.path.expanduser('~/.config/ai_credentials'))
from get_credential import get_credential

# Add reddit_sentiment_analyzer to path
reddit_analyzer_path = str(Path(__file__).parent.parent.parent / 'reddit_sentiment_analyzer')
sys.path.insert(0, reddit_analyzer_path)

# Import reddit analyzer modules
from modules.brand_selector import BrandSelector
from modules.google_search import GoogleSearcher
from modules.reddit_scraper import RedditScraper
from modules.data_processor import DataProcessor
from modules.behavioral_analysis import analyze_reddit_data


def run_section_research(app_name: str, section_name: str, prompt_file: str) -> dict:
    """
    Run analysis for any section
    Routes based on section_name to appropriate method

    Args:
        app_name: Name of the app (e.g., "Oura Ring")
        section_name: Section to analyze (e.g., "business_origin", "voice_of_customer")
        prompt_file: Path to prompt template (used for Perplexity sections)

    Returns:
        dict with 'section_name', 'app_name', 'markdown', 'json', 'citations'
    """

    # Route to appropriate handler based on section name
    if section_name == "voice_of_customer":
        return run_voice_of_customer_section(app_name, section_name)
    else:
        # All other sections use Perplexity
        return run_perplexity_section(app_name, section_name, prompt_file)


def run_perplexity_section(app_name: str, section_name: str, prompt_file: str) -> dict:
    """
    Run Perplexity-based research section
    Used for: business_origin, growth_loops, etc.
    """

    # Get API key
    api_key = get_credential("Perplexity API", "api_key")

    # Load prompt template
    with open(prompt_file, 'r') as f:
        prompt_template = f.read()

    # Replace placeholders
    prompt = prompt_template.replace("{{APP_NAME}}", app_name)

    # System messages by section
    system_messages = {
        "business_origin": "You are a startup historian and market anthropologist. Provide deep, evidence-based analysis of business origins and market conditions.",
        "growth_loops": "You are a growth systems architect combining Elena Verna–style loop thinking with anthropology, history, and behavioral economics. Analyze growth mechanics at a systems level."
    }

    system_content = system_messages.get(
        section_name,
        "You are an expert analyst. Provide deep, evidence-based analysis."
    )

    # API request
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 8000,
        "return_citations": True,
        "search_domain_filter": ["edu", "gov", "org"],
        "search_recency_filter": "year"
    }

    print(f"  🔍 {section_name.replace('_', ' ').title()}...")

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API request failed for {section_name}: {response.status_code}\n{response.text}")

    result = response.json()
    content = result['choices'][0]['message']['content']

    # Extract markdown and JSON
    markdown_section, json_section = extract_markdown_and_json(content)

    # Get citations
    citations = result.get('citations', [])

    # Add citations to markdown
    if citations:
        markdown_section += "\n\n## Sources\n\n"
        for i, citation in enumerate(citations, 1):
            markdown_section += f"{i}. {citation}\n"

    print(f"  ✅ {section_name.replace('_', ' ').title()} complete")

    return {
        "section_name": section_name,
        "app_name": app_name,
        "markdown": markdown_section,
        "json": json_section,
        "citations": citations
    }


def run_voice_of_customer_section(app_name: str, section_name: str) -> dict:
    """
    Run Voice of Customer section
    Uses Reddit data + Behavioral Analysis (OpenAI GPT-4o)
    """

    print(f"\n  📊 Voice of Customer Section for {app_name}")

    # Step 1: Collect Reddit data
    reddit_data = asyncio.run(collect_reddit_data(app_name))

    if not reddit_data:
        print(f"  ⚠️  No Reddit data found for {app_name}")
        return {
            'section_name': section_name,
            'app_name': app_name,
            'markdown': f"# Voice of Customer\n\nNo Reddit data found for {app_name}.",
            'json': {},
            'citations': []
        }

    # Step 2: Analyze with Behavioral Intelligence Framework
    analysis = analyze_reddit_data(app_name, reddit_data)

    return {
        'section_name': section_name,
        'app_name': app_name,
        'markdown': analysis['markdown'],
        'json': analysis['json'],
        'citations': []
    }


async def collect_reddit_data(app_name: str) -> list:
    """
    Collect Reddit data using reddit_sentiment_analyzer package
    """
    print(f"  🔍 Collecting Reddit data for {app_name}...")

    # Get or create prospect
    selector = BrandSelector()
    prospect = await selector.get_or_create_prospect(app_name)

    # Search Reddit URLs via Google
    searcher = GoogleSearcher()
    reddit_urls = await searcher.search_reddit_urls(app_name, "")
    print(f"  ✅ Found {len(reddit_urls)} Reddit URLs")

    # Store URLs in Supabase
    await searcher.update_prospect_urls(prospect['id'], reddit_urls, app_name)

    # Scrape Reddit posts/comments
    scraper = RedditScraper()
    posts_comments = await scraper.scrape_all_urls(reddit_urls, app_name, prospect['id'])
    print(f"  ✅ Scraped {len(posts_comments)} posts/comments")

    # Clean the data
    processor = DataProcessor()
    cleaned_data = await processor.process_data(posts_comments, app_name, prospect['id'])
    print(f"  ✅ Cleaned {len(cleaned_data)} valid items")

    return cleaned_data


def extract_markdown_and_json(content: str) -> tuple:
    """
    Extract markdown and JSON from AI response
    Returns: (markdown_str, json_dict)
    """
    markdown_section = ""
    json_section = {}

    if "```" in content:
        parts = content.split("```")
        markdown_section = parts[0].strip()

        # Find JSON in code fences
        for i, part in enumerate(parts[1:], 1):
            if i % 2 == 0:
                continue
            json_candidate = part.strip()
            if json_candidate.startswith('json'):
                json_candidate = json_candidate[4:].strip()

            try:
                if json_candidate.startswith('{'):
                    json_section = json.loads(json_candidate)
                    break
            except json.JSONDecodeError:
                continue
    else:
        markdown_section = content

    return markdown_section, json_section


if __name__ == "__main__":
    # Test standalone
    if len(sys.argv) < 3:
        print("Usage: python section_runner.py 'App Name' 'section_name' [prompt_file]")
        print("Example: python section_runner.py 'Oura Ring' 'voice_of_customer'")
        sys.exit(1)

    app_name = sys.argv[1]
    section_name = sys.argv[2]
    prompt_file = sys.argv[3] if len(sys.argv) > 3 else None

    result = run_section_research(app_name, section_name, prompt_file)

    print("\n" + "="*70)
    print(f"{section_name.replace('_', ' ').title().upper()} ANALYSIS")
    print("="*70)
    print(result['markdown'][:500] + "...")
