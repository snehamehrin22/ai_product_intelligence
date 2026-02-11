"""
Test script for carousel generation.

Usage:
    python scripts/generate_carousel.py <analysis_file.json> <angle_number>

Example:
    python scripts/generate_carousel.py data/analysis_outputs/eight_sleep_framework_analysis.json 1
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.carousel_generator import (
    generate_carousel,
    display_carousel
)
from src.carousel_pipeline.schemas import FrameworkAnalysis

load_dotenv()


def main():
    """Generate carousel from framework analysis."""

    if len(sys.argv) < 3:
        print("Usage: python scripts/generate_carousel.py <analysis_file.json> <angle_number>")
        print("\nExample:")
        print("  python scripts/generate_carousel.py data/analysis_outputs/eight_sleep_framework_analysis.json 1")
        print("\nAngle number: which carousel angle from the analysis (1, 2, or 3)")
        sys.exit(1)

    analysis_path = sys.argv[1]
    angle_index = int(sys.argv[2]) - 1  # Convert to 0-indexed

    # Load analysis
    print(f"\n📂 Loading analysis from: {analysis_path}")
    analysis_data = json.loads(Path(analysis_path).read_text(encoding="utf-8"))
    analysis = FrameworkAnalysis(**analysis_data)

    # Check angle exists
    if angle_index < 0 or angle_index >= len(analysis.carousel_angles):
        print(f"\n❌ Error: Angle {angle_index + 1} not found. Analysis has {len(analysis.carousel_angles)} angles.")
        print("\nAvailable angles:")
        for i, angle in enumerate(analysis.carousel_angles, 1):
            print(f"  {i}. {angle}")
        sys.exit(1)

    carousel_angle = analysis.carousel_angles[angle_index]

    # Extract product name from analysis path
    product_name = Path(analysis_path).stem.replace("_framework_analysis", "")

    # Generate output path
    output_path = f"data/carousel_outputs/{product_name}_carousel_angle_{angle_index + 1}.json"

    print("\n" + "="*70)
    print("🎨 CAROUSEL GENERATION")
    print("="*70)
    print(f"\nProduct: {product_name}")
    print(f"Angle: {carousel_angle}")
    print(f"Pillar: {analysis.pillar_id}")

    try:
        # Generate carousel
        carousel = generate_carousel(
            analysis=analysis,
            carousel_angle=carousel_angle,
            product_name=product_name,
            output_path=output_path
        )

        # Display
        display_carousel(carousel)

        print("\n✅ Carousel generated successfully!")
        print(f"📁 Saved to: {output_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
