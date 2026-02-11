"""
Test script for framework analysis.

Usage:
    python scripts/analyze_research.py <research_file.md>
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.framework_analyzer import (
    analyze_research,
    display_analysis_summary
)

load_dotenv()


def main():
    """Run framework analysis on research file."""

    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_research.py <research_file.md>")
        print("\nExample:")
        print("  python scripts/analyze_research.py '/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Content/Research/App Research/eight_sleep.md'")
        sys.exit(1)

    research_path = sys.argv[1]

    # Configuration
    pillar_id = "growth_loops_are_changing"
    framework_path = "prompts/frameworks/growth_loops_teardown_framework.md"

    # Generate output path
    research_name = Path(research_path).stem
    output_path = f"data/analysis_outputs/{research_name}_framework_analysis.json"

    print("\n" + "="*70)
    print("🔬 FRAMEWORK ANALYSIS")
    print("="*70)
    print(f"\nResearch: {Path(research_path).name}")
    print(f"Pillar: {pillar_id}")
    print(f"Framework: {framework_path}")

    try:
        # Run analysis
        analysis = analyze_research(
            research_path=research_path,
            pillar_id=pillar_id,
            framework_path=framework_path,
            output_path=output_path
        )

        # Display summary
        display_analysis_summary(analysis)

        print("\n✅ Analysis complete!")
        print(f"📁 Full analysis saved to: {output_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
