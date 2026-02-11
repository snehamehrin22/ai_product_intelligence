"""
Batch process all research files in a directory.

Generates 3 carousels (one per pillar) for each .md file found.

Usage:
    python scripts/batch_generate_carousels.py
    python scripts/batch_generate_carousels.py --no-tighten
    python scripts/batch_generate_carousels.py --input-dir "/custom/path"
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.multi_pillar_generator import generate_all_three_carousels

load_dotenv()


# Default input directory
DEFAULT_INPUT_DIR = "/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Content/Research/App Research"


def main():
    """Batch process all research files."""

    # Parse arguments
    use_tightening = True
    input_dir = DEFAULT_INPUT_DIR
    auto_confirm = False

    if "--no-tighten" in sys.argv:
        use_tightening = False

    if "--input-dir" in sys.argv:
        idx = sys.argv.index("--input-dir")
        if idx + 1 < len(sys.argv):
            input_dir = sys.argv[idx + 1]

    if "--auto" in sys.argv or "-y" in sys.argv:
        auto_confirm = True

    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)

    # Find all .md files
    research_files = list(input_path.glob("*.md"))

    if not research_files:
        print(f"❌ No .md files found in: {input_dir}")
        sys.exit(1)

    print("\n" + "="*70)
    print("📚 BATCH CAROUSEL GENERATION")
    print("="*70)
    print(f"\nInput directory: {input_dir}")
    print(f"Research files found: {len(research_files)}")
    print(f"Tightening: {'enabled' if use_tightening else 'disabled'}")
    print(f"\nFiles to process:")
    for f in research_files:
        print(f"  • {f.name}")

    if not auto_confirm:
        input("\n⏎  Press Enter to start processing...")

    # Process each file
    results = {}
    errors = {}

    for i, research_file in enumerate(research_files, 1):
        print("\n" + "="*70)
        print(f"[{i}/{len(research_files)}] Processing: {research_file.name}")
        print("="*70)

        try:
            carousels = generate_all_three_carousels(
                research_path=str(research_file),
                use_chatgpt_tightening=use_tightening
            )
            results[research_file.name] = carousels

        except Exception as e:
            print(f"\n❌ Error processing {research_file.name}: {e}")
            import traceback
            traceback.print_exc()
            errors[research_file.name] = str(e)

    # Summary
    print("\n\n" + "="*70)
    print("📊 BATCH PROCESSING COMPLETE")
    print("="*70)
    print(f"\n✅ Successfully processed: {len(results)}/{len(research_files)}")
    print(f"❌ Errors: {len(errors)}/{len(research_files)}")

    if results:
        print("\n✅ Successful:")
        for filename, carousels in results.items():
            print(f"\n  • {filename}")
            for pillar_id, carousel in carousels.items():
                print(f"    - {pillar_id}: {carousel.total_slides} slides")

    if errors:
        print("\n❌ Failed:")
        for filename, error in errors.items():
            print(f"  • {filename}: {error}")

    print(f"\n📁 All outputs saved to: data/carousel_outputs/")


if __name__ == "__main__":
    main()
