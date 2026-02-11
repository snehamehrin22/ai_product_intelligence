#!/usr/bin/env python3
"""
Parallel App Analysis Pipeline
Runs multiple analysis sections in parallel for speed

Usage:
    python run_pipeline.py "App Name"
    python run_pipeline.py "Oura Ring"
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add scripts to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from section_runner import run_section_research
from obsidian_publisher import publish_to_obsidian
from replit_publisher import publish_to_replit


def discover_prompts(prompts_dir):
    """Discover all numbered prompt files"""
    prompts = []
    for file in sorted(prompts_dir.glob("*.txt")):
        # Extract section name from filename (e.g., "01_business_origin.txt" -> "business_origin")
        filename = file.stem  # Remove .txt
        if filename[0].isdigit() and '_' in filename:
            section_name = '_'.join(filename.split('_')[1:])  # Remove number prefix
            prompts.append((section_name, file))
    return prompts


def run_parallel_analysis(app_name: str):
    """
    Run complete parallel analysis pipeline

    Args:
        app_name: Name of the app to analyze (e.g., "Oura Ring")
    """

    print("\n" + "="*70)
    print(f"🚀 PARALLEL APP ANALYSIS: {app_name}")
    print("="*70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'outputs' / f"{app_name.lower().replace(' ', '_')}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Run All Perplexity Sections in Parallel
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("\n" + "─"*70)
    print("STEP 1/3: PERPLEXITY PARALLEL RESEARCH")
    print("─"*70)

    # Discover all prompt sections
    prompts_dir = base_dir / 'prompts'
    sections = discover_prompts(prompts_dir)

    if not sections:
        print("❌ No prompt files found in prompts/")
        return False

    print(f"\n📋 Found {len(sections)} sections:")
    for section_name, _ in sections:
        print(f"   • {section_name.replace('_', ' ').title()}")

    print(f"\n⏳ Running {len(sections)} sections in parallel (this may take 30-60 seconds)...\n")

    # Run all sections in parallel
    section_results = {}
    with ThreadPoolExecutor(max_workers=len(sections)) as executor:
        # Submit all tasks
        future_to_section = {
            executor.submit(run_section_research, app_name, section_name, str(prompt_file)): section_name
            for section_name, prompt_file in sections
        }

        # Collect results as they complete
        for future in as_completed(future_to_section):
            section_name = future_to_section[future]
            try:
                result = future.result()
                section_results[section_name] = result
            except Exception as e:
                print(f"  ❌ {section_name.replace('_', ' ').title()} failed: {e}")
                import traceback
                traceback.print_exc()

    if not section_results:
        print("\n❌ All sections failed")
        return False

    print(f"\n✅ Completed {len(section_results)}/{len(sections)} sections successfully\n")

    # Save combined results
    for section_name, result in section_results.items():
        # Save individual section files
        section_dir = output_dir / section_name
        section_dir.mkdir(exist_ok=True)

        # Save markdown
        md_file = section_dir / f"{section_name}.md"
        with open(md_file, 'w') as f:
            f.write(result['markdown'])

        # Save JSON
        json_file = section_dir / f"{section_name}.json"
        with open(json_file, 'w') as f:
            json.dump(result['json'], f, indent=2)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Publish to Obsidian
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("─"*70)
    print("STEP 2/3: OBSIDIAN PUBLISHING")
    print("─"*70)

    try:
        # Combine all sections for Obsidian
        combined_markdown = ""
        combined_json = {}

        for section_name in sorted(section_results.keys()):
            result = section_results[section_name]
            combined_markdown += f"\n\n# {section_name.replace('_', ' ').title()}\n\n"
            combined_markdown += result['markdown']
            combined_json[section_name] = result['json']

        obsidian_note = publish_to_obsidian(combined_markdown, app_name, combined_json)
        print(f"✅ Published to Obsidian: {obsidian_note}")
    except Exception as e:
        print(f"⚠️  Obsidian publishing failed: {e}")
        print("   Continuing to Replit...")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Generate Replit YAML
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("\n" + "─"*70)
    print("STEP 3/3: REPLIT YAML GENERATION")
    print("─"*70)

    try:
        # Save combined JSON for Replit publisher
        combined_json_file = output_dir / f"{app_name.lower().replace(' ', '_')}_combined.json"
        with open(combined_json_file, 'w') as f:
            json.dump(combined_json, f, indent=2)

        yaml_file = publish_to_replit(str(combined_json_file), app_name, str(output_dir))
        print(f"✅ Replit YAML created: {yaml_file}")

        # Copy to ProductAnalyticsMaster if it exists
        replit_repo = Path.home() / 'Desktop' / 'ProductAnalyticsMaster' / 'case-studies'
        if replit_repo.exists():
            import shutil
            dest = replit_repo / f"{app_name.lower().replace(' ', '-')}.yaml"
            shutil.copy(yaml_file, dest)
            print(f"✅ Copied to Replit repo: {dest}")
            print(f"\n📝 Next: Push to GitHub:")
            print(f"   cd ~/Desktop/ProductAnalyticsMaster")
            print(f"   git add case-studies/{app_name.lower().replace(' ', '-')}.yaml")
            print(f"   git commit -m 'Add {app_name} analysis'")
            print(f"   git push")

    except Exception as e:
        print(f"⚠️  Replit YAML generation failed: {e}")
        import traceback
        traceback.print_exc()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COMPLETE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE")
    print("="*70)
    print(f"\n📁 Outputs saved to: {output_dir}")
    print(f"\n📊 Sections completed:")
    for section_name in sorted(section_results.keys()):
        print(f"   ✅ {section_name.replace('_', ' ').title()}")
    print(f"\n📄 Deliverables:")
    print(f"   ✅ Obsidian note")
    print(f"   ✅ Replit YAML")
    print(f"   ✅ Individual section files")

    return True


def main():
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("PARALLEL APP ANALYSIS PIPELINE")
        print("="*70)
        print("\nUsage: python run_pipeline.py 'App Name'")
        print("\nExample:")
        print("  python run_pipeline.py 'Oura Ring'")
        print("  python run_pipeline.py 'TikTok'")
        print("  python run_pipeline.py 'Spotify'")
        print("\nRequirements:")
        print("  1. BW_SESSION must be set (run: bw unlock)")
        print("  2. OBSIDIAN_VAULT_PATH environment variable")
        print("\nHow it works:")
        print("  • Discovers all prompts in prompts/ folder")
        print("  • Runs all sections in parallel for speed")
        print("  • Combines results into comprehensive analysis")
        print("="*70 + "\n")
        sys.exit(1)

    app_name = sys.argv[1]

    # Validate environment
    if not os.getenv('BW_SESSION'):
        print("\n❌ Error: BW_SESSION not set", file=sys.stderr)
        print("\nRun these commands first:")
        print("  bw unlock")
        print("  export BW_SESSION=\"your-session-key\"\n")
        sys.exit(1)

    # Run pipeline
    success = run_parallel_analysis(app_name)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
