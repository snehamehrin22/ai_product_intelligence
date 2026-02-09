"""
Automated carousel creation pipeline (non-interactive).

Runs the full pipeline automatically without user prompts.
Use this for testing or when you want immediate output.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.framework_analyzer import (
    analyze_research,
    display_analysis_summary
)
from src.carousel_pipeline.carousel_generator import (
    generate_carousel,
    display_carousel
)

load_dotenv()


def main():
    """Run automated carousel pipeline."""

    if len(sys.argv) < 2:
        print("Usage: python scripts/auto_carousel_pipeline.py <research_file.md> [angle_number]")
        print("\nExample:")
        print("  python scripts/auto_carousel_pipeline.py '/path/to/research.md'")
        print("  python scripts/auto_carousel_pipeline.py '/path/to/research.md' 2  # Use angle 2")
        sys.exit(1)

    research_path = sys.argv[1]
    angle_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1  # Default to angle 1
    research_name = Path(research_path).stem

    # Configuration
    pillar_id = "growth_loops_are_changing"
    framework_path = "prompts/frameworks/growth_loops_teardown_framework.md"

    print("\n" + "="*70)
    print("🚀 AUTOMATED CAROUSEL PIPELINE")
    print("="*70)
    print(f"\nProduct: {research_name}")
    print(f"Research: {Path(research_path).name}")
    print(f"Pillar: {pillar_id}")
    print(f"Selected angle: {angle_number}")

    # Output paths
    analysis_output = f"data/analysis_outputs/{research_name}_framework_analysis.json"
    carousel_output = f"data/carousel_outputs/{research_name}_carousel_angle_{angle_number}.json"

    try:
        # ====================================================================
        # STEP 1: Framework Analysis
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 1: FRAMEWORK ANALYSIS")
        print("="*70)

        analysis = analyze_research(
            research_path=research_path,
            pillar_id=pillar_id,
            framework_path=framework_path,
            output_path=analysis_output
        )

        display_analysis_summary(analysis)

        # ====================================================================
        # STEP 2: Select Carousel Angle
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 2: CAROUSEL ANGLE SELECTION")
        print("="*70)

        print(f"\nFramework identified {len(analysis.carousel_angles)} potential angles:")
        for i, angle in enumerate(analysis.carousel_angles, 1):
            print(f"  {i}. {angle}")

        # Validate angle number
        if angle_number < 1 or angle_number > len(analysis.carousel_angles):
            print(f"\n❌ Error: Angle {angle_number} not found. Analysis has {len(analysis.carousel_angles)} angles.")
            print("   Re-run with valid angle number (1-{})".format(len(analysis.carousel_angles)))
            sys.exit(1)

        carousel_angle = analysis.carousel_angles[angle_number - 1]
        print(f"\n✓ Using angle {angle_number}: {carousel_angle}")

        # ====================================================================
        # STEP 3: Generate Carousel
        # ====================================================================
        print("\n\n" + "="*70)
        print("STEP 3: CAROUSEL GENERATION")
        print("="*70)

        carousel = generate_carousel(
            analysis=analysis,
            carousel_angle=carousel_angle,
            product_name=research_name,
            output_path=carousel_output
        )

        display_carousel(carousel)

        # ====================================================================
        # STEP 4: Summary
        # ====================================================================
        print("\n\n" + "="*70)
        print("✅ PIPELINE COMPLETE")
        print("="*70)
        print(f"\n📁 Files generated:")
        print(f"   • Analysis: {analysis_output}")
        print(f"   • Carousel: {carousel_output}")
        print(f"\n🎯 Next steps:")
        print(f"   • Review the carousel JSON")
        print(f"   • Try different angles: python scripts/auto_carousel_pipeline.py '{research_path}' [1-{len(analysis.carousel_angles)}]")
        print(f"   • Run interactive mode for feedback: python scripts/interactive_carousel_pipeline.py '{research_path}'")

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
