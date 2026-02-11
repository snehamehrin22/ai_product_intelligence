"""
Test script for the cognitive block splitter.
Run from project root: python scripts/test_splitter.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path so we can import notes_agent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notes_agent.splitter import split_into_blocks


def main():
    """Test the splitter on sample input."""
    # Load sample text
    sample_path = Path(__file__).parent.parent / "tests" / "inputs" / "sample_01.txt"

    if not sample_path.exists():
        print(f"❌ Error: Sample file not found at {sample_path}")
        return

    raw_text = sample_path.read_text(encoding="utf-8")
    print(f"📄 Loaded {len(raw_text)} chars from {sample_path.name}\n")

    # Split into blocks
    print("🤖 Splitting into cognitive blocks...\n")

    try:
        blocks = split_into_blocks(raw_text)

        # Display results
        print(f"✅ Split into {len(blocks)} blocks:\n")
        print("=" * 80)

        for block in blocks:
            print(f"\n[{block.block_id}] {block.block_name}")
            print("-" * 80)
            print(f"{block.block_text[:200]}...")
            print()

        print("=" * 80)
        print(f"\n✓ All blocks validated with Pydantic schema")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
