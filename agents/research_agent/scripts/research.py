#!/usr/bin/env python3
"""
Research Agent - Investigate observations using Perplexity Sonar.

Usage:
    python scripts/research.py --text "Your observation here"
    python scripts/research.py --id T042
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from research_agent.schemas import ResearchInput, ResearchOutput
from research_agent.tools_perplexity import research_with_perplexity
from research_agent.tools_supabase import get_observation
from research_agent.utils import load_prompt


def main():
    """Main entry point for research agent."""
    parser = argparse.ArgumentParser(description="Research observations using Perplexity")
    parser.add_argument("--text", type=str, help="Direct observation text to research")
    parser.add_argument("--id", type=str, help="Supabase observation ID (e.g., T042)")
    parser.add_argument("--output", type=str, help="Output markdown file path (optional)")

    args = parser.parse_args()

    # Validate input
    if not args.text and not args.id:
        parser.error("Must provide either --text or --id")
    if args.text and args.id:
        parser.error("Provide either --text or --id, not both")

    # Get observation text
    observation_text = None
    if args.text:
        observation_text = args.text
        print(f"\n🔍 Researching observation: {observation_text[:100]}...")
    elif args.id:
        print(f"\n🔍 Fetching observation {args.id} from Supabase...")
        obs_data = get_observation(args.id)
        if not obs_data:
            print(f"❌ Observation {args.id} not found in Supabase")
            sys.exit(1)
        observation_text = obs_data.get('raw_context', '')
        print(f"✅ Found: {observation_text[:100]}...")

    # Load prompt template
    prompt_template = load_prompt("research_prompt")

    # Format query
    query = prompt_template.replace("{observation}", observation_text)

    # Research with Perplexity
    print("\n🤖 Researching with Perplexity Sonar...")
    try:
        result = research_with_perplexity(query)

        # Build markdown output
        md_output = f"""# Research Findings

## Observation
{observation_text}

---

## Research Results

{result.findings}

---

## Metadata
- **Model**: {result.metadata.get('model')}
- **Tokens Used**: {result.metadata.get('tokens_used')}
- **Query**: {result.query[:200]}...
"""

        if result.sources:
            md_output += "\n\n## Sources\n"
            for i, source in enumerate(result.sources, 1):
                md_output += f"{i}. {source}\n"

        # Save to file if output specified
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(md_output, encoding='utf-8')
            print(f"\n✅ Research saved to: {args.output}")
        else:
            # Display results
            print("\n" + "="*80)
            print("📊 RESEARCH FINDINGS")
            print("="*80)
            print(result.findings)
            print("\n" + "="*80)

            if result.sources:
                print("\n📚 SOURCES:")
                for i, source in enumerate(result.sources, 1):
                    print(f"{i}. {source}")

            print(f"\n📈 Metadata:")
            print(f"  Model: {result.metadata.get('model')}")
            print(f"  Tokens: {result.metadata.get('tokens_used')}")

    except Exception as e:
        print(f"\n❌ Research failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
