"""
Unified Event Extractor

Extracts events from all three sources and saves to unified format.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import EventCollection

# Import extractors
try:
    from extract_eventbrite import extract_eventbrite_events
except ImportError as e:
    print(f"⚠️  Could not import Eventbrite extractor: {e}")
    extract_eventbrite_events = None

try:
    from extract_luma import extract_luma_events
except ImportError as e:
    print(f"⚠️  Could not import Luma extractor: {e}")
    extract_luma_events = None

try:
    from extract_meetup import extract_meetup_events
except ImportError as e:
    print(f"⚠️  Could not import Meetup extractor: {e}")
    extract_meetup_events = None


def main():
    print("=" * 60)
    print("TORONTO EVENTS EXTRACTION")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%I:%M %p')}\n")

    all_events = []
    sources_used = []

    # Extract from Eventbrite
    if extract_eventbrite_events:
        try:
            eventbrite_events = extract_eventbrite_events(limit=50)
            all_events.extend(eventbrite_events)
            sources_used.append("eventbrite")
        except Exception as e:
            print(f"⚠️  Eventbrite extraction failed: {e}\n")
    else:
        print("⚠️  Eventbrite extractor not available\n")

    # Extract from Luma
    if extract_luma_events:
        try:
            luma_events = extract_luma_events(limit=50)
            all_events.extend(luma_events)
            sources_used.append("luma")
        except Exception as e:
            print(f"⚠️  Luma extraction failed: {e}\n")
    else:
        print("⚠️  Luma extractor not available\n")

    # Extract from Meetup
    if extract_meetup_events:
        try:
            meetup_events = extract_meetup_events(limit=50)
            all_events.extend(meetup_events)
            sources_used.append("meetup")
        except Exception as e:
            print(f"⚠️  Meetup extraction failed: {e}\n")
    else:
        print("⚠️  Meetup extractor not available\n")

    # Create collection
    collection = EventCollection(
        events=all_events,
        total_count=len(all_events),
        sources=sources_used,
        city="Toronto"
    )

    # Save to file
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "events_toronto.json"

    with open(output_file, "w") as f:
        json.dump(collection.model_dump(mode="json"), f, indent=2, default=str)

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Total events extracted: {len(all_events)}")
    print(f"Sources used: {', '.join(sources_used)}")
    print(f"Saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%I:%M %p')}")

    # Breakdown by source
    if all_events:
        print("\nBreakdown by source:")
        for source in ["eventbrite", "luma", "meetup"]:
            count = sum(1 for e in all_events if e.source == source)
            if count > 0:
                print(f"  {source.title()}: {count} events")


if __name__ == "__main__":
    main()
