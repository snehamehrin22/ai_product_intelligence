"""
Meetup GraphQL API Extractor

Uses Meetup GraphQL API to fetch Toronto events.
Docs: https://www.meetup.com/graphql/
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

MEETUP_API_KEY = os.getenv("MEETUP_API_KEY")
GRAPHQL_ENDPOINT = "https://api.meetup.com/gql"


def get_headers() -> dict:
    """Get authenticated headers for Meetup GraphQL API"""
    if not MEETUP_API_KEY:
        raise ValueError("MEETUP_API_KEY not set in .env file")

    return {
        "Authorization": f"Bearer {MEETUP_API_KEY}",
        "Content-Type": "application/json"
    }


def search_events_query(city: str = "Toronto", limit: int = 50) -> str:
    """
    Build GraphQL query to search for events.

    This is a template - adjust based on actual Meetup GraphQL schema.
    Check https://www.meetup.com/graphql/ for the exact schema.
    """

    query = f"""
    query {{
      keywordSearch(input: {{
        query: "{city}"
        first: {limit}
      }}) {{
        edges {{
          node {{
            result {{
              ... on Event {{
                id
                title
                description
                dateTime
                endTime
                going
                eventUrl
                venue {{
                  name
                  address
                  city
                  state
                  lat
                  lng
                }}
                group {{
                  name
                  urlname
                }}
                images {{
                  baseUrl
                }}
                isFree
              }}
            }}
          }}
        }}
      }}
    }}
    """

    return query


def execute_graphql_query(query: str) -> Optional[dict]:
    """Execute a GraphQL query against Meetup API"""

    payload = {
        "query": query
    }

    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers=get_headers(),
            timeout=15
        )
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            print(f"⚠️  GraphQL errors: {data['errors']}")
            return None

        return data.get("data")

    except requests.exceptions.HTTPError as e:
        print(f"⚠️  Meetup API error: {e}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return None

    except Exception as e:
        print(f"❌ Error querying Meetup: {e}")
        return None


def parse_meetup_event(event_data: dict) -> Optional[Event]:
    """Parse Meetup GraphQL response into our Event model"""

    try:
        event_id = event_data.get("id")
        title = event_data.get("title", "Unknown Event")
        description = event_data.get("description")
        url = event_data.get("eventUrl", "")

        # Time
        date_time_str = event_data.get("dateTime")
        start_time = datetime.fromisoformat(date_time_str.replace("Z", "+00:00")) if date_time_str else None

        end_time_str = event_data.get("endTime")
        end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00")) if end_time_str else None

        # Location
        venue = event_data.get("venue", {})
        location_name = venue.get("name")
        address = venue.get("address")
        city = venue.get("city")
        latitude = venue.get("lat")
        longitude = venue.get("lng")

        # Group (organizer)
        group = event_data.get("group", {})
        organizer_name = group.get("name")

        # Attendees
        going = event_data.get("going", 0)

        # Pricing
        is_free = event_data.get("isFree", True)

        # Image
        images = event_data.get("images", [])
        image_url = images[0].get("baseUrl") if images else None

        return Event(
            id=str(event_id),
            source="meetup",
            url=url,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location_name=location_name,
            address=address,
            city=city,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            organizer_name=organizer_name,
            organizer_type="Group",
            attendee_count=going,
            is_free=is_free,
            currency="USD",
            image_url=image_url
        )

    except Exception as e:
        print(f"⚠️  Error parsing Meetup event: {e}")
        return None


def extract_meetup_events(city: str = "Toronto", limit: int = 50) -> List[Event]:
    """Main extraction function"""

    print("\n👥 Extracting Meetup Events...")
    print(f"   City: {city}")
    print(f"   Limit: {limit}")

    # Build and execute query
    query = search_events_query(city, limit)
    result = execute_graphql_query(query)

    if not result:
        print("   ❌ No results from Meetup")
        return []

    # Extract events from GraphQL response
    edges = result.get("keywordSearch", {}).get("edges", [])

    events = []
    for edge in edges:
        event_data = edge.get("node", {}).get("result", {})
        if event_data:
            event = parse_meetup_event(event_data)
            if event:
                events.append(event)

    print(f"   ✅ Extracted {len(events)} events")
    return events


if __name__ == "__main__":
    # Test the extractor
    events = extract_meetup_events()

    if events:
        print(f"\n📋 Sample Event:")
        print(f"   Title: {events[0].title}")
        print(f"   Time: {events[0].start_time}")
        print(f"   Location: {events[0].location_name}")
        print(f"   Group: {events[0].organizer_name}")
