"""
Luma API Extractor

Uses Luma API to fetch Toronto events.
Docs: https://docs.luma.com/reference/getting-started-with-your-api
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

LUMA_API_KEY = os.getenv("LUMA_API_KEY")
BASE_URL = "https://api.lu.ma"  # Check Luma docs for exact base URL


def get_headers() -> dict:
    """Get authenticated headers for Luma API"""
    if not LUMA_API_KEY:
        raise ValueError("LUMA_API_KEY not set in .env file")

    return {
        "x-luma-api-key": LUMA_API_KEY,  # Check Luma docs for exact header name
        "Content-Type": "application/json"
    }


def list_calendar_events(calendar_id: Optional[str] = None, limit: int = 50) -> List[dict]:
    """
    List events from a calendar or discovery feed.

    Note: You'll need to check Luma's actual API docs for:
    - How to search public events by location
    - Whether you need a calendar_id or can query globally
    - Pagination format
    """

    # This is a guess - check actual Luma API docs
    url = f"{BASE_URL}/public/v1/calendar/list-events"

    params = {
        "city": "Toronto",
        "limit": limit
    }

    if calendar_id:
        params["calendar_id"] = calendar_id

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        events = data.get("entries", [])  # Check actual response structure

        print(f"✅ Found {len(events)} events from Luma")
        return events

    except requests.exceptions.HTTPError as e:
        print(f"⚠️  Luma API error: {e}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return []

    except Exception as e:
        print(f"❌ Error searching Luma: {e}")
        return []


def get_event_details(event_id: str) -> Optional[dict]:
    """Get detailed information for a single event"""

    url = f"{BASE_URL}/public/v1/event/get"

    params = {"event_id": event_id}

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"⚠️  Could not fetch Luma event {event_id}: {e}")
        return None


def parse_luma_event(event_data: dict) -> Optional[Event]:
    """Parse Luma API response into our Event model"""

    try:
        # This structure is based on the JSON-LD we saw earlier
        # Adjust according to actual Luma API response

        event_id = event_data.get("api_id") or event_data.get("event_id")
        name = event_data.get("name")
        url = event_data.get("url", f"https://lu.ma/{event_id}")

        # Time
        start_time = datetime.fromisoformat(event_data.get("start_at", "").replace("Z", "+00:00"))
        end_at = event_data.get("end_at")
        end_time = datetime.fromisoformat(end_at.replace("Z", "+00:00")) if end_at else None

        # Location
        geo_address = event_data.get("geo_address_json", {})
        location_name = geo_address.get("name") or event_data.get("location", {}).get("name")
        city = geo_address.get("city_state")
        latitude = geo_address.get("latitude")
        longitude = geo_address.get("longitude")

        # Organizer
        host = event_data.get("host", {})
        organizer_name = host.get("name")

        # Pricing
        tickets = event_data.get("tickets", [])
        is_free = all(t.get("price", {}).get("cents") == 0 for t in tickets) if tickets else True

        # Image
        image_url = event_data.get("cover_url")

        return Event(
            id=str(event_id),
            source="luma",
            url=url,
            title=name,
            start_time=start_time,
            end_time=end_time,
            location_name=location_name,
            city=city,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            organizer_name=organizer_name,
            is_free=is_free,
            currency="USD",
            image_url=image_url
        )

    except Exception as e:
        print(f"⚠️  Error parsing Luma event: {e}")
        return None


def extract_luma_events(limit: int = 50) -> List[Event]:
    """Main extraction function"""

    print("\n🌟 Extracting Luma Events...")
    print(f"   Limit: {limit}")

    # List events
    raw_events = list_calendar_events(limit=limit)

    # Parse into our Event model
    events = []
    for raw_event in raw_events:
        event = parse_luma_event(raw_event)
        if event:
            events.append(event)

    print(f"   ✅ Extracted {len(events)} events")
    return events


if __name__ == "__main__":
    # Test the extractor
    events = extract_luma_events()

    if events:
        print(f"\n📋 Sample Event:")
        print(f"   Title: {events[0].title}")
        print(f"   Time: {events[0].start_time}")
        print(f"   Location: {events[0].location_name}")
