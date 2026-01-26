#!/usr/bin/env python3
"""
Obsidian Publisher
Takes Perplexity research output and publishes to Obsidian vault
"""

import sys
import os
from pathlib import Path
from datetime import datetime


def publish_to_obsidian(markdown_content: str, app_name: str, json_data: dict = None):
    """
    Publish analysis to Obsidian vault

    Args:
        markdown_content: The markdown analysis from Perplexity
        app_name: Name of the app
        json_data: Optional structured JSON data

    Returns:
        Path to created Obsidian note
    """

    # Get Obsidian vault path from environment
    vault_path = os.getenv('OBSIDIAN_VAULT_PATH')

    if not vault_path:
        raise ValueError(
            "OBSIDIAN_VAULT_PATH environment variable not set.\n"
            "Set it with: export OBSIDIAN_VAULT_PATH='/path/to/your/vault'"
        )

    vault_path = Path(vault_path)

    if not vault_path.exists():
        raise ValueError(f"Obsidian vault not found at: {vault_path}")

    # Create folder structure: App Analysis/[App Name]/
    analysis_folder = vault_path / "App Analysis" / app_name
    analysis_folder.mkdir(parents=True, exist_ok=True)

    # Create note filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    note_filename = f"{app_name} - Business Origin Analysis.md"
    note_path = analysis_folder / note_filename

    # Build Obsidian note with frontmatter
    frontmatter = f"""---
app: {app_name}
analysis_type: Business Origin & World-State
date: {timestamp}
source: Perplexity Deep Research
tags:
  - app-analysis
  - business-origin
  - {app_name.lower().replace(' ', '-')}
---

"""

    # Add title
    title = f"# {app_name} - Business Origin Analysis\n\n"

    # Add metadata section
    metadata = f"""## Metadata
- **App**: {app_name}
- **Analysis Date**: {timestamp}
- **Source**: Perplexity Deep Research (sonar-pro model)
- **Analysis Type**: Business Origin & World-State

---

"""

    # Combine all sections
    full_note = frontmatter + title + metadata + markdown_content

    # Write to Obsidian vault
    with open(note_path, 'w') as f:
        f.write(full_note)

    print(f"✅ Published to Obsidian:")
    print(f"   📁 {analysis_folder}")
    print(f"   📄 {note_filename}")

    return note_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publish_to_obsidian.py 'App Name' 'path/to/markdown.md'")
        print("Example: python publish_to_obsidian.py 'Flo Health' '../outputs/flo_test/flo_health_analysis.md'")
        sys.exit(1)

    app_name = sys.argv[1]
    markdown_file = sys.argv[2]

    # Read markdown content
    with open(markdown_file, 'r') as f:
        markdown_content = f.read()

    try:
        note_path = publish_to_obsidian(markdown_content, app_name)
        print(f"\n📝 Obsidian note created at:")
        print(f"   {note_path}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
