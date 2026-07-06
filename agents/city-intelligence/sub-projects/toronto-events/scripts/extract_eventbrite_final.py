"""
Eventbrite Extractor (JSON-LD from public page)

Since the API endpoint for event search doesn't exist,
we extract JSON-LD structured data from Eventbrite's public Toronto events page.
"""

import requests
import json
import re
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event


def extract_json_ld(html: str) -> List[dict]:
    """Extract JSON-LD structured data from HTML"""
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


def parse_eventbrite_event(event_data: dict) -> Optional[Event]:
    """Parse Eventbrite JSON-LD event into our Event model"""

    try:
        event_id = event_data.get("@id", "").split("/")[-1] or event_data.get("url", "").split("/")[-1]
        title = event_data.get("name", "Unknown Event")
        description = event_data.get("description")
        url = event_data.get("url", "")

        # Time
        start_str = event_data.get("startDate", "")
        start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00")) if start_str else None

        end_str = event_data.get("endDate")
        end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None

        # Location
        location = event_data.get("location", {})
        if isinstance(location, dict):
            location_name = location.get("name")
            address_data = location.get("address", {})
            if isinstance(address_data, dict):
                address = address_data.get("streetAddress")
                city = address_data.get("addressLocality", "Toronto")
            else:
                address = None
                city = "Toronto"
        else:
            location_name = None
            address = None
            city = "Toronto"

        # Pricing
        offers = event_data.get("offers", [])
        if isinstance(offers, list) and offers:
            first_offer = offers[0]
            is_free = first_offer.get("price", 0) == 0 or first_offer.get("price") == "0"
            price = float(first_offer.get("price", 0)) if not is_free else None
        else:
            is_free = True
            price = None

        # Image
        image = event_data.get("image")
        if isinstance(image, list):
            image_url = image[0] if image else None
        else:
            image_url = image

        # Organizer
        organizer = event_data.get("organizer", {})
        if isinstance(organizer, dict):
            organizer_name = organizer.get("name")
        else:
            organizer_name = None

        if not start_time:
            return None  # Skip events without start time

        return Event(
            id=event_id,
            source="eventbrite",
            url=url,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location_name=location_name,
            address=address,
            city=city,
            is_online=False,  # Assume in-person unless specified
            organizer_name=organizer_name,
            organizer_type="Organization",
            is_free=is_free,
            price=price,
            currency="CAD",
            image_url=image_url
        )

    except Exception as e:
        print(f"⚠️  Error parsing event: {e}")
        return None


def extract_eventbrite_events(limit: int = 100) -> List[Event]:
    """Extract events from Eventbrite Toronto public page"""

    print("\n🎫 Extracting Eventbrite Events (JSON-LD)...")

    try:
        url = "https://www.eventbrite.ca/d/canada--toronto/events/"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Extract JSON-LD
        json_ld_objects = extract_json_ld(response.text)

        events = []
        for obj in json_ld_objects:
            # Check if this is an Event object
            if obj.get("@type") == "Event":
                event = parse_eventbrite_event(obj)
                if event:
                    events.append(event)
                    if len(events) >= limit:
                        break

        print(f"   ✅ Extracted {len(events)} events")
        return events

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


if __name__ == "__main__":
    events = extract_eventbrite_events(limit=50)

    if events:
        print(f"\n📋 Sample Events:")
        for i, event in enumerate(events[:3], 1):
            print(f"\n{i}. {event.title}")
            print(f"   Time: {event.start_time}")
            print(f"   Location: {event.location_name or 'TBD'}")
            print(f"   Free: {event.is_free}")
