#!/usr/bin/env python3
"""
Behavioral Intelligence Analysis
Transforms Reddit data into rigorous behavioral intelligence memo
using multi-lens framework for product strategy
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Add credentials path
sys.path.append(os.path.expanduser('~/.config/ai_credentials'))
from get_credential import get_credential

import requests


def analyze_reddit_data(app_name: str, reddit_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze Reddit data using behavioral intelligence framework

    Args:
        app_name: Name of the app
        reddit_data: List of cleaned Reddit posts/comments

    Returns:
        dict with 'markdown' (full memo) and 'json' (structured data)
    """

    print(f"  🧠 Running behavioral intelligence analysis for {app_name}...")

    # Get API key from Bitwarden (using OpenAI for deep analysis)
    api_key = get_credential("Open AI", "api_key")

    # Prepare Reddit data for analysis
    data_summary = prepare_reddit_data_summary(reddit_data)

    # Get metadata
    metadata = extract_metadata(app_name, reddit_data)

    # Create the behavioral analysis prompt
    prompt = create_behavioral_analysis_prompt(app_name, data_summary, metadata)

    # Call OpenAI API
    response = call_openai_api(api_key, prompt)

    # Parse response
    markdown = response
    json_data = extract_json_from_response(response)

    print(f"  ✅ Behavioral analysis complete")

    return {
        'markdown': markdown,
        'json': json_data
    }


def prepare_reddit_data_summary(reddit_data: List[Dict[str, Any]]) -> str:
    """Format Reddit data for analysis"""

    # Sort by date and upvotes
    sorted_data = sorted(
        reddit_data,
        key=lambda x: (x.get('upVotes', 0), x.get('createdAt', '')),
        reverse=True
    )

    # Take top 50 most relevant posts
    top_posts = sorted_data[:50]

    summary = ""
    for i, post in enumerate(top_posts, 1):
        summary += f"\n---\n[Post {i}]\n"
        summary += f"Subreddit: {post.get('subreddit', 'Unknown')}\n"
        summary += f"Date: {post.get('createdAt', 'Unknown')}\n"
        summary += f"Upvotes: {post.get('upVotes', 0)}\n"
        summary += f"Text: {post.get('text', '')}\n"

    return summary


def extract_metadata(app_name: str, reddit_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract metadata about the dataset"""

    if not reddit_data:
        return {}

    # Get date range
    dates = [post.get('createdAt') for post in reddit_data if post.get('createdAt')]
    dates = [d for d in dates if d]  # Remove None values

    # Get subreddits
    subreddits = list(set([post.get('subreddit') for post in reddit_data if post.get('subreddit')]))

    return {
        'app_name': app_name,
        'total_posts': len(reddit_data),
        'date_start': min(dates) if dates else 'Unknown',
        'date_end': max(dates) if dates else 'Unknown',
        'subreddits': subreddits,
        'analysis_date': datetime.now().strftime('%Y-%m-%d')
    }


def create_behavioral_analysis_prompt(app_name: str, data_summary: str, metadata: Dict[str, Any]) -> str:
    """Create the full behavioral analysis prompt by reading from template file"""

    # Read prompt template from app_analysis_system
    prompt_file = Path(__file__).parent.parent.parent / 'app_analysis_system' / 'prompts' / '03_voice_of_customer.txt'

    with open(prompt_file, 'r') as f:
        template = f.read()

    # Replace placeholders with actual data
    prompt = f"""INPUT DATA

App: {app_name}
Total Posts: {metadata.get('total_posts', 'Unknown')}
Date Range: {metadata.get('date_start', 'Unknown')} → {metadata.get('date_end', 'Unknown')}
Subreddits: {', '.join(metadata.get('subreddits', []))}

REDDIT DATA:
{data_summary}

---

{template}"""

    # Replace template variables
    prompt = prompt.replace('{APP_NAME}', app_name)
    prompt = prompt.replace('{ANALYSIS_DATE}', metadata.get('analysis_date', 'Unknown'))
    prompt = prompt.replace('{TOTAL_POSTS}', str(metadata.get('total_posts', 'Unknown')))
    prompt = prompt.replace('{DATE_START}', metadata.get('date_start', 'Unknown'))
    prompt = prompt.replace('{DATE_END}', metadata.get('date_end', 'Unknown'))
    prompt = prompt.replace('{SUBREDDITS}', ', '.join(metadata.get('subreddits', [])))

    return prompt


def call_openai_api(api_key: str, prompt: str) -> str:
    """Call OpenAI API for analysis"""

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "You are a Senior Product Data Scientist + Behavioral Scientist + Cultural Intelligence Analyst. You produce rigorous, evidence-based intelligence memos for growth leaders."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 16000
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code}\n{response.text}")

    result = response.json()
    content = result['choices'][0]['message']['content']

    return content


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract structured JSON data from response if present"""

    # Try to find JSON in code fences
    if "```json" in response or "```" in response:
        parts = response.split("```")
        for i, part in enumerate(parts[1:], 1):
            if i % 2 == 0:
                continue
            json_candidate = part.strip()
            if json_candidate.startswith('json'):
                json_candidate = json_candidate[4:].strip()

            try:
                if json_candidate.startswith('{'):
                    return json.loads(json_candidate)
            except json.JSONDecodeError:
                continue

    return {}


if __name__ == "__main__":
    print("Behavioral Analysis Module")
    print("Use this module to analyze Reddit data with multi-lens behavioral framework")
