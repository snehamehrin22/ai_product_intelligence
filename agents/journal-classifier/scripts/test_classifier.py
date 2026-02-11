"""
Test script for the block classifier.
Run from project root: python scripts/test_classifier.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path so we can import notes_agent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notes_agent.splitter import split_into_blocks
from notes_agent.classifiers.llm_classifier import classify_block
from notes_agent.schemas import ClassifiedBlock


def main():
    """Test the classifier on sample input."""
    # Load sample text
    sample_path = Path(__file__).parent.parent / "tests" / "inputs" / "sample_01.txt"

    if not sample_path.exists():
        print(f"❌ Error: Sample file not found at {sample_path}")
        return

    raw_text = sample_path.read_text(encoding="utf-8")
    print(f"📄 Loaded {len(raw_text)} chars from {sample_path.name}\n")

    # Split into blocks
    print("🔪 Splitting into cognitive blocks...")
    blocks = split_into_blocks(raw_text)
    print(f"✓ Got {len(blocks)} blocks\n")

    # Classify first 3 blocks
    print("🤖 Classifying blocks...\n")
    print("=" * 80)

    for block in blocks[:3]:
        try:
            # Classify with LLM
            classification = classify_block(block)

            # Create classified block
            classified = ClassifiedBlock(
                block=block,
                classification=classification
            )

            # Display results
            print(f"\n[{block.block_id}] {block.block_name}")
            print("-" * 80)
            print(f"Text: {block.block_text[:150]}...")
            print(f"\nClassification:")
            print(f"  Themes: {', '.join(classification.themes)}")
            print(f"  Core Emotion: {classification.core_emotion}")
            print(f"  Nervous System State: {classification.nervous_system_state}")
            print(f"  Behavioral Response: {classification.behavioral_response}")
            print(f"  Fear Underneath: {classification.fear_underneath or 'null'}")
            print(f"  Self-Concept Gap: {classification.self_concept_gap or 'null'}")
            print(f"  Action Signal: {classification.action_signal}")
            print(f"  Action Note: {classification.action_note or 'null'}")
            print(f"  Confidence: {classification.confidence}")
            print()

        except Exception as e:
            print(f"\n❌ Error classifying block {block.block_id}: {e}")
            import traceback
            traceback.print_exc()

    print("=" * 80)
    print(f"\n✓ All blocks validated with Pydantic schemas")


if __name__ == "__main__":
    main()
