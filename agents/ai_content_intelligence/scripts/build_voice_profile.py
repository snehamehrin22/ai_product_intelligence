#!/usr/bin/env python3
"""
Build voice profile from training carousel samples.

Usage:
    python scripts/build_voice_profile.py

Prerequisites:
    1. Add 5-7 carousel samples to data/training_carousels/
       Name them: carousel_01.txt, carousel_02.txt, etc.
    2. Set ANTHROPIC_API_KEY in your .env file

Output:
    - config/voice_profile.json (validated schema)
    - config/voice_analysis_raw.json (full Claude analysis)
    - prompts/writing_style_system.txt (prompt for content generation)
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from carousel_pipeline.voice_profile import build_voice_profile


def main():
    """Main entry point."""
    print("=" * 60)
    print("VOICE PROFILE BUILDER")
    print("=" * 60)
    print()

    try:
        profile = build_voice_profile(
            training_dir="data/training_carousels",
            output_path="config/voice_profile.json"
        )

        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review config/voice_profile.json")
        print("2. Review prompts/writing_style_system.txt")
        print("3. Test with: python scripts/test_voice_profile.py")
        print()

    except FileNotFoundError as e:
        print()
        print("ERROR:", str(e))
        print()
        print("Setup instructions:")
        print("1. Create directory: mkdir -p data/training_carousels")
        print("2. Add carousel samples (5-7 minimum):")
        print("   - Name them: carousel_01.txt, carousel_02.txt, etc.")
        print("   - Each file should contain the full carousel text")
        print("   - Include hook, body slides, and CTA")
        print("3. Run this script again")
        print()
        sys.exit(1)

    except ValueError as e:
        print()
        print("ERROR:", str(e))
        print()
        if "API" in str(e):
            print("Add ANTHROPIC_API_KEY to your .env file")
        print()
        sys.exit(1)

    except Exception as e:
        print()
        print("UNEXPECTED ERROR:", str(e))
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
