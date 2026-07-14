"""
Meetup Extractor using Apify
Uses Apify's Meetup scraper to get events
"""

import json
import subprocess
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event


def parse_meetup_event(event_data: dict) -> Optional[Event]:
    """Parse Meetup event into our Event model"""

    try:
        event_id = event_data.get("eventId", "")
        title = event_data.get("eventName", "Unknown Event")
        description = event_data.get("eventDescription", "")
        url = event_data.get("eventUrl", "")

        # Time (format: "2026-06-02T17:30:00-04:00")
        date_str = event_data.get("date", "")
        start_time = datetime.fromisoformat(date_str) if date_str else None

        # Location
        address = event_data.get("address", "")
        event_type = event_data.get("eventType", "PHYSICAL")
        is_online = event_type == "ONLINE"

        # Organizer
        organizer_name = event_data.get("organizedByGroup", "")

        # Pricing
        is_paid = event_data.get("isPaidEvent", False)
        is_free = not is_paid
        price = float(event_data.get("feeAmount", 0)) if is_paid else None
        currency = event_data.get("feeCurrency", "CAD")

        # Capacity
        max_attendees = event_data.get("maxAttendees")
        actual_attendees = event_data.get("actualAttendees", 0)

        if not start_time:
            return None  # Skip events without start time

        return Event(
            id=event_id,
            source="meetup",
            url=url,
            title=title,
            description=description,
            start_time=start_time,
            end_time=None,  # Meetup doesn't provide end time
            location_name=address,
            address=address,
            city="Toronto",
            is_online=is_online,
            organizer_name=organizer_name,
            organizer_type="Community",
            is_free=is_free,
            price=price,
            currency=currency if is_paid else None,
            image_url=None,
            tags=[organizer_name] if organizer_name else [],
        )

    except Exception as e:
        print(f"⚠️  Error parsing event: {e}")
        return None


def extract_meetup_events(city: str = "toronto", country: str = "canada", max_results: int = 50) -> List[Event]:
    """Extract events from Meetup using Apify CLI"""

    print("\n🤝 Extracting Meetup Events (via Apify)...")

    try:
        # Prepare input JSON
        input_json = json.dumps({
            "searchKeyword": "",
            "city": city,
            "state": "ON" if country == "canada" else "",
            "country": country,
            "maxResults": max_results
        })

        # Run Apify CLI
        print(f"   📡 Fetching events from Meetup...")
        result = subprocess.run(
            f'echo \'{input_json}\' | ~/.apify/bin/apify call filip_cicvarek/meetup-scraper --silent --output-dataset',
            shell=True,
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            print(f"   ❌ Error running Apify CLI: {result.stderr}")
            return []

        # Parse JSON output
        meetup_events = json.loads(result.stdout)
        print(f"   ✅ Retrieved {len(meetup_events)} events from Meetup")

        # Convert to our Event model
        events = []
        for event_data in meetup_events:
            event = parse_meetup_event(event_data)
            if event:
                events.append(event)

        print(f"   ✅ Parsed {len(events)} events")
        return events

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    events = extract_meetup_events(city="toronto", country="canada", max_results=50)

    if events:
        print(f"\n📋 Sample Events:")
        for i, event in enumerate(events[:5], 1):
            print(f"\n{i}. {event.title}")
            print(f"   Time: {event.start_time}")
            print(f"   Organizer: {event.organizer_name}")
            print(f"   Free: {event.is_free}")
            print(f"   Online: {event.is_online}")

        # Save to file
        output_dir = Path(__file__).parent.parent / "data" / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "events_meetup.json"

        with open(output_file, "w") as f:
            json.dump([e.model_dump(mode="json") for e in events], f, indent=2, default=str)

        print(f"\n💾 Saved {len(events)} events to {output_file}")
    else:
        print("\n❌ No events extracted")
