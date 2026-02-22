"""
Test script for Layer 1 Triage Agent.
Processes all sample files in tests/inputs/ directory.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notes_agent.layer1_triage import triage_braindump


def main():
    """Process all sample files and output results."""
    # Find all sample files
    inputs_dir = Path(__file__).parent.parent / "tests" / "inputs"
    sample_files = sorted(inputs_dir.glob("sample_*.txt"))

    if not sample_files:
        print("❌ No sample files found in tests/inputs/")
        print("Create files like: tests/inputs/sample_01.txt")
        return

    print(f"\n{'='*80}")
    print(f"LAYER 1 TRIAGE TEST")
    print(f"{'='*80}\n")
    print(f"Found {len(sample_files)} sample file(s)\n")

    all_items = []
    starting_id = 1

    for sample_file in sample_files:
        print(f"\n{'─'*80}")
        print(f"Processing: {sample_file.name}")
        print(f"{'─'*80}\n")

        # Read input
        raw_text = sample_file.read_text(encoding="utf-8").strip()

        if not raw_text or raw_text.startswith("Put your"):
            print(f"⏭️  Skipping {sample_file.name} (placeholder content)\n")
            continue

        print(f"Input preview: {raw_text[:200]}...\n")

        # Triage
        try:
            items = triage_braindump(
                raw_text=raw_text,
                date=datetime.now().strftime("%Y-%m-%d"),
                starting_id=starting_id
            )

            # Print results
            print(f"📋 Results for {sample_file.name}:")
            print(f"{'─'*80}")
            for item in items:
                print(f"\n[{item.id}] {item.type}")
                print(f"  Domain: {item.domain}")
                print(f"  Text: {item.raw_context[:100]}...")
                print(f"  Tags: {item.tags}")
                print(f"  Niche: {item.niche_signal} | Publishable: {item.publishable}")

            all_items.extend(items)
            starting_id += len(items)

        except Exception as e:
            print(f"❌ Error processing {sample_file.name}: {e}\n")
            continue

    # Summary
    print(f"\n\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total items: {len(all_items)}")

    if all_items:
        # Count by type
        type_counts = {}
        for item in all_items:
            type_counts[item.type] = type_counts.get(item.type, 0) + 1

        print(f"\nBy type:")
        for item_type, count in sorted(type_counts.items()):
            print(f"  {item_type}: {count}")

        # Niche signals
        niche_count = sum(1 for item in all_items if item.niche_signal)
        pub_count = sum(1 for item in all_items if item.publishable)
        print(f"\nNiche signals: {niche_count}/{len(all_items)} ({niche_count/len(all_items)*100:.1f}%)")
        print(f"Publishable: {pub_count}/{len(all_items)} ({pub_count/len(all_items)*100:.1f}%)")

        # Save to file
        output_file = Path(__file__).parent.parent / "tests" / "output_layer1.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([item.model_dump() for item in all_items], f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved results to: {output_file}")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
