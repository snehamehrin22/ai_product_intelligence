"""
Phase 2 & 3: Extract events from all sources

Strategy: Extract JSON-LD structured data from HTML pages
Time: 20 minutes (12:45-1:05 PM)
"""

import requests
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event, EventCollection

# Setup
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"


def extract_json_ld(html: str) -> List[Dict[str, Any]]:
    """Extract JSON-LD structured data from HTML"""
    # Find all <script type="application/ld+json"> tags
    pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL)

    json_objects = []
    for match in matches:
        try:
            data = json.loads(match)
            json_objects.append(data)
        except json.JSONDecodeError:
            continue

    return json_objects


def extract_luma_events() -> List[Event]:
    """Extract events from Luma"""
    print("\n🌟 Extracting Luma events...")

    try:
        url = "https://lu.ma/toronto"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Extract JSON-LD data
        json_ld_objects = extract_json_ld(response.text)

        events = []
        for obj in json_ld_objects:
            # Look for ItemList with events
            if obj.get("@type") == "ItemList":
                for item in obj.get("itemListElement", []):
                    event_data = item.get("item", {})
                    if event_data.get("@type") == "Event":
                        try:
                            # Parse the event
                            event = Event(
                                id=event_data.get("@id", "").split("/")[-1],
                                source="luma",
                                url=event_data.get("url", ""),
                                title=event_data.get("name", "Unknown Event"),
                                description=None,  # Not in JSON-LD
                                start_time=datetime.fromisoformat(event_data.get("startDate", "").replace("Z", "+00:00")),
                                end_time=datetime.fromisoformat(event_data.get("endDate", "").replace("Z", "+00:00")) if event_data.get("endDate") else None,
                                location_name=event_data.get("location", {}).get("name"),
                                city=event_data.get("location", {}).get("address", {}).get("addressLocality"),
                                latitude=event_data.get("location", {}).get("geo", {}).get("latitude"),
                                longitude=event_data.get("location", {}).get("geo", {}).get("longitude"),
                                organizer_name=event_data.get("organizer", [{}])[0].get("name") if event_data.get("organizer") else None,
                                organizer_type="Organization" if event_data.get("organizer", [{}])[0].get("@type") == "Organization" else "Person",
                                is_free=event_data.get("offers", [{}])[0].get("price", 0) == 0,
                                price=float(event_data.get("offers", [{}])[0].get("price", 0)) if event_data.get("offers") else None,
                                availability=event_data.get("offers", [{}])[0].get("availability", "").split("/")[-1] if event_data.get("offers") else None,
                                image_url=event_data.get("image", [None])[0] if event_data.get("image") else None,
                            )
                            events.append(event)
                        except Exception as e:
                            print(f"  ⚠️  Skipped event: {e}")
                            continue

        print(f"  ✅ Extracted {len(events)} events from Luma")
        return events

    except Exception as e:
        print(f"  ❌ Error extracting Luma events: {e}")
        return []


def extract_eventbrite_events() -> List[Event]:
    """Extract events from Eventbrite"""
    print("\n🎫 Extracting Eventbrite events...")

    try:
        # Try public events page
        url = "https://www.eventbrite.ca/d/canada--toronto/events/"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Extract JSON-LD if available
        json_ld_objects = extract_json_ld(response.text)

        events = []
        for obj in json_ld_objects:
            if obj.get("@type") == "Event":
                try:
                    event = Event(
                        id=obj.get("@id", "unknown"),
                        source="eventbrite",
                        url=obj.get("url", ""),
                        title=obj.get("name", "Unknown Event"),
                        description=obj.get("description"),
                        start_time=datetime.fromisoformat(obj.get("startDate", "").replace("Z", "+00:00")),
                        end_time=datetime.fromisoformat(obj.get("endDate", "").replace("Z", "+00:00")) if obj.get("endDate") else None,
                        location_name=obj.get("location", {}).get("name"),
                        city="Toronto",  # Assume Toronto since we're on Toronto page
                        is_free=obj.get("isAccessibleForFree", True),
                        image_url=obj.get("image"),
                    )
                    events.append(event)
                except Exception as e:
                    print(f"  ⚠️  Skipped event: {e}")
                    continue

        print(f"  ✅ Extracted {len(events)} events from Eventbrite")
        return events

    except Exception as e:
        print(f"  ❌ Error extracting Eventbrite events: {e}")
        return []


def extract_meetup_events() -> List[Event]:
    """Extract events from Meetup"""
    print("\n👥 Extracting Meetup events...")

    try:
        url = "https://www.meetup.com/find/?location=ca--on--toronto&source=EVENTS"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Extract JSON-LD
        json_ld_objects = extract_json_ld(response.text)

        events = []
        # Meetup structure might be different, adapt as needed
        # For now, return empty to keep moving
        print(f"  ⚠️  Meetup extraction needs more time - skipping for MVP")
        return events

    except Exception as e:
        print(f"  ❌ Error extracting Meetup events: {e}")
        return []


def main():
    print("=" * 60)
    print("PHASE 2 & 3: Event Extraction")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%I:%M %p')}")

    # Extract from all sources
    all_events = []

    luma_events = extract_luma_events()
    all_events.extend(luma_events)

    eventbrite_events = extract_eventbrite_events()
    all_events.extend(eventbrite_events)

    meetup_events = extract_meetup_events()
    all_events.extend(meetup_events)

    # Create collection
    collection = EventCollection(
        events=all_events,
        total_count=len(all_events),
        sources=["luma", "eventbrite", "meetup"],
        city="Toronto"
    )

    # Save to processed data
    output_file = DATA_PROCESSED / "events_toronto.json"
    with open(output_file, "w") as f:
        json.dump(collection.model_dump(mode="json"), f, indent=2, default=str)

    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Total events extracted: {len(all_events)}")
    print(f"  - Luma: {len(luma_events)}")
    print(f"  - Eventbrite: {len(eventbrite_events)}")
    print(f"  - Meetup: {len(meetup_events)}")
    print(f"\n💾 Saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%I:%M %p')}")
    print("\n📋 Next: Analyze patterns")


if __name__ == "__main__":
    main()
