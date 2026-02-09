#!/usr/bin/env python3
"""
Convert Obsidian markdown files to Replit YAML format
Uses GPT-4o to extract structured data from markdown
"""

import sys
import os
import yaml
from pathlib import Path

# Add credentials path
sys.path.append(os.path.expanduser('~/.config/ai_credentials'))
from get_credential import get_credential

import requests


def markdown_to_yaml(markdown_file: str, app_name: str, output_dir: str) -> str:
    """
    Convert markdown analysis to YAML case study format

    Args:
        markdown_file: Path to markdown file
        app_name: Name of the app
        output_dir: Directory to save YAML

    Returns:
        Path to generated YAML file
    """

    print(f"\n{'='*70}")
    print(f"Converting {app_name} markdown to YAML")
    print(f"{'='*70}\n")

    # Read markdown
    with open(markdown_file, 'r') as f:
        markdown_content = f.read()

    print(f"✅ Read {len(markdown_content)} characters from {markdown_file}")

    # Get API key
    api_key = get_credential("Open AI", "api_key")

    # Create prompt for GPT-4o
    prompt = f"""You are a data extraction expert. Convert this markdown analysis into structured YAML format matching the template structure.

MARKDOWN ANALYSIS:
{markdown_content[:30000]}  # Limit to avoid token limits

TASK:
Extract key information and create a YAML case study with these sections:
1. title, description, client, industry, tags
2. sections array with different section types

OUTPUT FORMAT:
Return ONLY valid YAML (no markdown code fences, no explanations).

Example structure:
```yaml
title: "{app_name}: Analysis"
description: "Analysis of {app_name}"
client: "{app_name}"
industry: "Technology"
tags: ["Analysis"]
sections:
  - type: title
    badge: "ANALYSIS"
    main_title: "{app_name}"
    subtitle: "..."
```

Extract as much detail as possible from the markdown. Focus on business_origin, growth loops, and voice of customer sections if present.
"""

    # Call OpenAI API
    print("🤖 Calling GPT-4o to structure the data...")

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
                "content": "You are a YAML generation expert. Return ONLY valid YAML, no markdown code fences, no explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 16000
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code}\n{response.text}")

    result = response.json()
    yaml_content = result['choices'][0]['message']['content']

    # Clean up any markdown code fences
    if yaml_content.startswith('```yaml'):
        yaml_content = yaml_content[7:]
    if yaml_content.startswith('```'):
        yaml_content = yaml_content[3:]
    if yaml_content.endswith('```'):
        yaml_content = yaml_content[:-3]
    yaml_content = yaml_content.strip()

    print("✅ Generated YAML structure")

    # Save YAML
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    yaml_filename = f"{app_name.lower().replace(' ', '-')}.yaml"
    yaml_file = output_path / yaml_filename

    with open(yaml_file, 'w') as f:
        f.write(yaml_content)

    print(f"✅ Saved to: {yaml_file}")

    # Copy to ProductAnalyticsMaster if exists
    replit_repo = Path.home() / 'Desktop' / 'ProductAnalyticsMaster' / 'case-studies'
    if replit_repo.exists():
        import shutil
        dest = replit_repo / yaml_filename
        shutil.copy(yaml_file, dest)
        print(f"✅ Copied to Replit repo: {dest}")

    return str(yaml_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python markdown_to_yaml.py 'markdown_file.md' 'App Name' [output_dir]")
        print("Example: python markdown_to_yaml.py 'Eight Sleep.md' 'Eight Sleep' '../outputs'")
        sys.exit(1)

    markdown_file = sys.argv[1]
    app_name = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else './outputs'

    try:
        yaml_file = markdown_to_yaml(markdown_file, app_name, output_dir)
        print(f"\n✅ Conversion complete!")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
