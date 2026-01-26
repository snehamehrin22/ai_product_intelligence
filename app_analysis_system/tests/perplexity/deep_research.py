#!/usr/bin/env python3
"""
Perplexity Deep Research API Integration
Uses business_origin.txt prompt to analyze apps
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add credentials path
sys.path.append(os.path.expanduser('~/.config/ai_credentials'))
from get_credential import get_credential


def load_prompt_template():
    """Load the business origin prompt template"""
    prompt_path = Path(__file__).parent / 'prompts' / 'business_origin.txt'
    with open(prompt_path, 'r') as f:
        return f.read()


def run_deep_research(app_name: str, output_dir: str = None) -> dict:
    """
    Run Perplexity deep research on an app

    Args:
        app_name: Name of the app to analyze (e.g., "Flo Health")
        output_dir: Optional directory to save response

    Returns:
        dict with 'markdown' and 'json' keys containing the analysis
    """

    # Get API key from Bitwarden
    api_key = get_credential("Perplexity API", "api_key")

    # Load prompt template
    prompt_template = load_prompt_template()

    # Replace {{APP_NAME}} with actual app name
    prompt = prompt_template.replace("{{APP_NAME}}", app_name)

    # Prepare API request
    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",  # Deep research model
        "messages": [
            {
                "role": "system",
                "content": "You are a startup historian and market anthropologist. Provide deep, evidence-based analysis of business origins and market conditions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 8000,  # Long-form analysis
        "return_citations": True,
        "search_domain_filter": ["edu", "gov", "org"],  # Prioritize quality sources
        "search_recency_filter": "year"  # Focus on recent data
    }

    print(f"\n🔍 Running deep research on: {app_name}")
    print(f"📊 Model: sonar-pro")
    print(f"⏳ This may take 30-60 seconds...\n")

    # Make API request
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}\n{response.text}")

    result = response.json()

    # Extract response
    content = result['choices'][0]['message']['content']

    # Extract markdown and JSON from response
    # The response should contain both markdown analysis and JSON object
    markdown_section = ""
    json_section = {}

    # Try to find JSON in code fence (look for ```json or just ``` with { })
    if "```" in content:
        # Split by code fences
        parts = content.split("```")

        # First part is markdown
        markdown_section = parts[0].strip()

        # Try to find JSON in code fences
        for i, part in enumerate(parts[1:], 1):
            # Skip the closing fence
            if i % 2 == 0:
                continue
            # Remove 'json' if present at start
            json_candidate = part.strip()
            if json_candidate.startswith('json'):
                json_candidate = json_candidate[4:].strip()

            # Try to parse as JSON
            try:
                if json_candidate.startswith('{'):
                    json_section = json.loads(json_candidate)
                    break
            except json.JSONDecodeError:
                continue
    else:
        # If no code fence, use entire content as markdown
        markdown_section = content

    # Get citations if available
    citations = result.get('citations', [])

    # Add citations to markdown
    if citations:
        markdown_section += "\n\n## Sources\n\n"
        for i, citation in enumerate(citations, 1):
            markdown_section += f"{i}. {citation}\n"

    # Prepare output
    output = {
        "app_name": app_name,
        "markdown": markdown_section,
        "json": json_section,
        "citations": citations,
        "raw_response": result
    }

    # Save to file if output_dir specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save markdown
        markdown_file = output_path / f"{app_name.lower().replace(' ', '_')}_analysis.md"
        with open(markdown_file, 'w') as f:
            f.write(markdown_section)

        # Save JSON
        json_file = output_path / f"{app_name.lower().replace(' ', '_')}_data.json"
        with open(json_file, 'w') as f:
            json.dump(json_section, f, indent=2)

        # Save full response
        full_file = output_path / f"{app_name.lower().replace(' ', '_')}_full_response.json"
        with open(full_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"✅ Saved outputs to: {output_path}")
        print(f"   📄 {markdown_file.name}")
        print(f"   📊 {json_file.name}")
        print(f"   🗂️  {full_file.name}")

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deep_research.py 'App Name' [output_dir]")
        print("Example: python deep_research.py 'Flo Health' '../outputs/flo'")
        sys.exit(1)

    app_name = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = run_deep_research(app_name, output_dir)
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print("\nMarkdown Preview (first 500 chars):")
        print(result['markdown'][:500] + "...")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
