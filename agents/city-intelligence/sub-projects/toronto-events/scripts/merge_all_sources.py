"""
Merge events from all sources (Luma, Eventbrite, Meetup)
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event, EventCollection


def load_meetup_raw():
    """Load and parse raw Meetup data"""
    meetup_file = Path(__file__).parent.parent / "data" / "raw" / "meetup_june_raw.json"

    if not meetup_file.exists():
        print("⚠️  No Meetup data found")
        return []

    with open(meetup_file) as f:
        meetup_data = json.load(f)

    events = []
    for event_data in meetup_data:
        try:
            event_id = event_data.get("eventId", "")
            title = event_data.get("eventName", "Unknown Event")
            description = event_data.get("eventDescription", "")
            url = event_data.get("eventUrl", "")

            date_str = event_data.get("date", "")
            start_time = datetime.fromisoformat(date_str) if date_str else None

            address = event_data.get("address", "")
            event_type = event_data.get("eventType", "PHYSICAL")
            is_online = event_type == "ONLINE"

            organizer_name = event_data.get("organizedByGroup", "")

            is_paid = event_data.get("isPaidEvent", False)
            is_free = not is_paid
            price = float(event_data.get("feeAmount", 0)) if is_paid else None
            currency = event_data.get("feeCurrency") or "CAD"

            if not start_time:
                continue

            event = Event(
                id=event_id,
                source="meetup",
                url=url,
                title=title,
                description=description,
                start_time=start_time,
                end_time=None,
                location_name=address,
                address=address,
                city="Toronto",
                is_online=is_online,
                organizer_name=organizer_name,
                organizer_type="Community",
                is_free=is_free,
                price=price,
                currency=currency,
                image_url=None,
                tags=[organizer_name] if organizer_name else [],
            )
            events.append(event)

        except Exception as e:
            print(f"⚠️  Error parsing Meetup event: {e}")
            continue

    return events


def load_existing_events(source: str):
    """Load events from a source file"""
    file_path = Path(__file__).parent.parent / "data" / "processed" / f"events_{source}.json"

    if not file_path.exists():
        return []

    with open(file_path) as f:
        data = json.load(f)

    # Handle both list and dict formats
    if isinstance(data, dict) and "events" in data:
        events_data = data["events"]
    elif isinstance(data, list):
        events_data = data
    else:
        return []

    events = []
    for event_data in events_data:
        try:
            event = Event(**event_data)
            events.append(event)
        except Exception as e:
            print(f"⚠️  Error loading {source} event: {e}")
            continue

    return events


def main():
    print("==" * 30)
    print("MERGING ALL EVENT SOURCES")
    print("==" * 30)

    all_events = []
    sources_used = []

    # Load Luma events
    print("\n📅 Loading Luma events...")
    luma_events = load_existing_events("toronto")
    if luma_events:
        # Filter only Luma events
        luma_events = [e for e in luma_events if e.source == "luma"]
        all_events.extend(luma_events)
        sources_used.append("luma")
        print(f"   ✅ Loaded {len(luma_events)} Luma events")

    # Load Meetup events
    print("\n🤝 Loading Meetup events...")
    meetup_events = load_meetup_raw()
    if meetup_events:
        all_events.extend(meetup_events)
        sources_used.append("meetup")
        print(f"   ✅ Loaded {len(meetup_events)} Meetup events")

    # Load Eventbrite events (if available)
    print("\n🎫 Loading Eventbrite events...")
    eventbrite_events = load_existing_events("eventbrite")
    if eventbrite_events:
        all_events.extend(eventbrite_events)
        sources_used.append("eventbrite")
        print(f"   ✅ Loaded {len(eventbrite_events)} Eventbrite events")
    else:
        print("   ⚠️  No Eventbrite events found (still rate limited)")

    # Remove duplicates (by ID)
    seen_ids = set()
    unique_events = []
    for event in all_events:
        if event.id not in seen_ids:
            seen_ids.add(event.id)
            unique_events.append(event)

    print(f"\n📊 Total unique events: {len(unique_events)}")

    # Create collection
    collection = EventCollection(
        events=unique_events,
        total_count=len(unique_events),
        sources=sources_used,
        city="Toronto"
    )

    # Save merged file
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "events_all_sources.json"

    with open(output_file, "w") as f:
        json.dump(collection.model_dump(mode="json"), f, indent=2, default=str)

    print(f"\n💾 Saved to: {output_file}")

    # Breakdown by source
    print("\n📊 Breakdown by source:")
    for source in ["luma", "meetup", "eventbrite"]:
        count = sum(1 for e in unique_events if e.source == source)
        if count > 0:
            print(f"   {source.title()}: {count} events")

    # Date range
    if unique_events:
        dates = [e.start_time for e in unique_events if e.start_time]
        if dates:
            # Convert all to naive datetime for comparison
            dates_naive = []
            for d in dates:
                if d.tzinfo:
                    dates_naive.append(d.replace(tzinfo=None))
                else:
                    dates_naive.append(d)

            min_date = min(dates_naive).strftime("%B %d, %Y")
            max_date = max(dates_naive).strftime("%B %d, %Y")
            print(f"\n📅 Date range: {min_date} to {max_date}")

    # Sample events
    print("\n📋 Sample events:")
    for i, event in enumerate(unique_events[:5], 1):
        print(f"\n{i}. {event.title}")
        print(f"   Source: {event.source}")
        print(f"   Date: {event.start_time.strftime('%b %d, %Y at %I:%M %p')}")
        print(f"   Organizer: {event.organizer_name}")
        print(f"   Free: {event.is_free}")


if __name__ == "__main__":
    main()
