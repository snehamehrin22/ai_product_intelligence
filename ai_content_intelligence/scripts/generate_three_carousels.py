"""
Generate 3 carousels from a single research file (one per pillar).

Usage:
    python scripts/generate_three_carousels.py <research_file.md>
    python scripts/generate_three_carousels.py <research_file.md> --pillar pillar_01
    python scripts/generate_three_carousels.py <research_file.md> --no-tighten
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.multi_pillar_generator import (
    generate_all_three_carousels,
    generate_carousel_for_pillar
)

load_dotenv()


def main():
    """Run multi-pillar carousel generation."""

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_three_carousels.py <research_file.md>")
        print("\nOptions:")
        print("  --pillar <pillar_id>   Generate only specific pillar (pillar_01, pillar_02, or pillar_03)")
        print("  --no-tighten           Skip ChatGPT prose tightening stage")
        print("\nExamples:")
        print("  python scripts/generate_three_carousels.py '/path/to/Superhuman.md'")
        print("  python scripts/generate_three_carousels.py '/path/to/Superhuman.md' --pillar pillar_01")
        print("  python scripts/generate_three_carousels.py '/path/to/Superhuman.md' --no-tighten")
        sys.exit(1)

    research_path = sys.argv[1]

    # Parse optional arguments
    pillar_only = None
    use_tightening = True

    if "--pillar" in sys.argv:
        pillar_idx = sys.argv.index("--pillar")
        if pillar_idx + 1 < len(sys.argv):
            pillar_only = sys.argv[pillar_idx + 1]
            if pillar_only not in ["pillar_01", "pillar_02", "pillar_03"]:
                print(f"❌ Invalid pillar: {pillar_only}")
                print("   Must be one of: pillar_01, pillar_02, pillar_03")
                sys.exit(1)

    if "--no-tighten" in sys.argv:
        use_tightening = False

    # Validate research file
    if not Path(research_path).exists():
        print(f"❌ Research file not found: {research_path}")
        sys.exit(1)

    try:
        # Generate single pillar or all three
        if pillar_only:
            print(f"\n🎯 Generating carousel for {pillar_only} only")
            print(f"   Research: {Path(research_path).name}")
            print(f"   Tightening: {'enabled' if use_tightening else 'disabled'}")

            carousel = generate_carousel_for_pillar(
                research_path=research_path,
                pillar_id=pillar_only,
                use_chatgpt_tightening=use_tightening
            )

            # Save output
            research_name = Path(research_path).stem
            output_dir = Path("data/carousel_outputs")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get pillar metadata for filename
            from src.carousel_pipeline.prompt_builder import get_pillar_metadata
            pillar_meta = get_pillar_metadata(pillar_only)
            pillar_slug = pillar_meta["id"]

            # Save JSON
            json_path = output_dir / f"{research_name}_{pillar_only}_{pillar_slug}.json"
            import json
            json_path.write_text(
                json.dumps(carousel.model_dump(), indent=2, default=str),
                encoding="utf-8"
            )

            # Save XML
            from src.carousel_pipeline.multi_pillar_generator import build_xml_from_carousel
            xml_path = output_dir / f"{research_name}_{pillar_only}_{pillar_slug}.xml"
            xml_content = build_xml_from_carousel(carousel)
            xml_path.write_text(xml_content, encoding="utf-8")

            print(f"\n✅ Carousel generated successfully!")
            print(f"📁 Output:")
            print(f"   • {json_path}")
            print(f"   • {xml_path}")

        else:
            # Generate all three
            results = generate_all_three_carousels(
                research_path=research_path,
                use_chatgpt_tightening=use_tightening
            )

            print(f"\n📊 Summary:")
            for pillar_id, carousel in results.items():
                print(f"   • {pillar_id}: {carousel.total_slides} slides")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
