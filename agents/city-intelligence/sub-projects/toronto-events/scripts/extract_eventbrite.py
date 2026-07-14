"""
Eventbrite API Extractor

Uses Eventbrite REST API v3 to fetch Toronto events.
Docs: https://www.eventbrite.com/platform/docs/introduction
"""

import os
import requests
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event

# Load environment variables
load_dotenv()

EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")
BASE_URL = "https://www.eventbriteapi.com/v3"


def get_headers() -> dict:
    """Get authenticated headers for Eventbrite API"""
    if not EVENTBRITE_TOKEN:
        raise ValueError("EVENTBRITE_TOKEN not set in .env file")

    return {
        "Authorization": f"Bearer {EVENTBRITE_TOKEN}",
        "Content-Type": "application/json"
    }


def search_events(location: str = "Toronto, ON, Canada", limit: int = 50) -> List[dict]:
    """
    Search for events in a location.

    Note: The search endpoint varies - you might need to:
    1. Search by organization if you have org IDs
    2. Use event discovery endpoints
    3. Or search public events

    For now, we'll try the events search endpoint.
    """

    # Eventbrite search can be done via:
    # - GET /events/search/ (if available)
    # - Or by getting events from known organizations

    # Try event search endpoint
    url = f"{BASE_URL}/events/search/"

    params = {
        "location.address": location,
        "location.within": "25km",  # 25km radius
        "expand": "venue,organizer,ticket_availability",
        "page_size": limit,
        "status": "live"  # Only live events
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        events = data.get("events", [])

        print(f"✅ Found {len(events)} events from Eventbrite")
        return events

    except requests.exceptions.HTTPError as e:
        print(f"⚠️  Eventbrite API error: {e}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return []

    except Exception as e:
        print(f"❌ Error searching Eventbrite: {e}")
        return []


def get_event_details(event_id: str) -> Optional[dict]:
    """
    Get detailed information for a single event.

    GET /v3/events/{event_id}/
    """
    url = f"{BASE_URL}/events/{event_id}/"

    params = {
        "expand": "venue,organizer,ticket_availability,category"
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"⚠️  Could not fetch event {event_id}: {e}")
        return None


def parse_eventbrite_event(event_data: dict) -> Optional[Event]:
    """Parse Eventbrite API response into our Event model"""

    try:
        # Extract basic info
        event_id = event_data.get("id")
        name = event_data.get("name", {}).get("text", "Unknown Event")
        description = event_data.get("description", {}).get("text")
        url = event_data.get("url", "")

        # Time
        start_time = datetime.fromisoformat(event_data.get("start", {}).get("utc", "").replace("Z", "+00:00"))
        end_time_str = event_data.get("end", {}).get("utc")
        end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00")) if end_time_str else None

        # Location
        venue = event_data.get("venue", {})
        location_name = venue.get("name")
        address = venue.get("address", {}).get("localized_address_display")
        city = venue.get("address", {}).get("city")
        latitude = venue.get("latitude")
        longitude = venue.get("longitude")

        is_online = event_data.get("online_event", False)

        # Organizer
        organizer = event_data.get("organizer", {})
        organizer_name = organizer.get("name")

        # Pricing
        is_free = event_data.get("is_free", True)

        # Category
        category = event_data.get("category", {}).get("name") if event_data.get("category") else None

        # Image
        image_url = event_data.get("logo", {}).get("url") if event_data.get("logo") else None

        # Capacity
        capacity = event_data.get("capacity")

        return Event(
            id=event_id,
            source="eventbrite",
            url=url,
            title=name,
            description=description,
            category=category,
            start_time=start_time,
            end_time=end_time,
            location_name=location_name,
            address=address,
            city=city,
            is_online=is_online,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            organizer_name=organizer_name,
            organizer_type="Organization",  # Eventbrite uses organizations
            capacity=capacity,
            is_free=is_free,
            currency="USD",  # Eventbrite default
            image_url=image_url
        )

    except Exception as e:
        print(f"⚠️  Error parsing Eventbrite event: {e}")
        return None


def extract_eventbrite_events(location: str = "Toronto, ON, Canada", limit: int = 50) -> List[Event]:
    """Main extraction function"""

    print("\n🎫 Extracting Eventbrite Events...")
    print(f"   Location: {location}")
    print(f"   Limit: {limit}")

    # Search for events
    raw_events = search_events(location, limit)

    # Parse into our Event model
    events = []
    for raw_event in raw_events:
        event = parse_eventbrite_event(raw_event)
        if event:
            events.append(event)

    print(f"   ✅ Extracted {len(events)} events")
    return events


if __name__ == "__main__":
    # Test the extractor
    events = extract_eventbrite_events()

    if events:
        print(f"\n📋 Sample Event:")
        print(f"   Title: {events[0].title}")
        print(f"   Time: {events[0].start_time}")
        print(f"   Location: {events[0].location_name}")
        print(f"   Free: {events[0].is_free}")
