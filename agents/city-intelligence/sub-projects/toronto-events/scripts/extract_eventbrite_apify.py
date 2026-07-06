"""
Eventbrite Extractor using Apify
Uses Apify's web scraping infrastructure to avoid rate limits
"""

import os
import json
import re
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event

from apify_client import ApifyClient


def extract_json_ld_from_html(html: str) -> List[dict]:
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
            is_online=False,
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


def extract_eventbrite_events_with_apify(limit: int = 100) -> List[Event]:
    """Extract events from Eventbrite using Apify"""

    print("\n🎫 Extracting Eventbrite Events (via Apify)...")

    # Initialize Apify client
    client = ApifyClient(os.environ.get("APIFY_API_TOKEN", "apify_api_NMI3QOCmSbtzuhnh9W7T4vFr1RqeE21TgVjr"))

    # URL to scrape
    url = "https://www.eventbrite.ca/d/canada--toronto/events/"

    try:
        # Run the web scraper
        print(f"   📡 Fetching page via Apify...")
        run_input = {
            "startUrls": [{"url": url}],
            "maxRequestRetries": 3,
            "maxConcurrency": 1,
        }

        # Use the website content crawler (needs fewer permissions)
        run = client.actor("apify/website-content-crawler").call(run_input=run_input)

        # Get the HTML from results
        print(f"   🔍 Extracting JSON-LD data...")

        # Fetch the results from the default dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        if not dataset_items:
            print("   ⚠️  No data returned from Apify")
            return []

        # Debug: print what we got
        print(f"   📊 Got {len(dataset_items)} items from Apify")
        print(f"   🔑 Keys in first item: {list(dataset_items[0].keys())}")

        # Get the HTML content from first result
        html_content = dataset_items[0].get("html", "") or dataset_items[0].get("text", "") or dataset_items[0].get("markdown", "")

        print(f"   📏 HTML content length: {len(html_content)} characters")

        # Extract JSON-LD
        json_ld_objects = extract_json_ld_from_html(html_content)

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
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # Set token
    os.environ["APIFY_API_TOKEN"] = "apify_api_NMI3QOCmSbtzuhnh9W7T4vFr1RqeE21TgVjr"

    events = extract_eventbrite_events_with_apify(limit=50)

    if events:
        print(f"\n📋 Sample Events:")
        for i, event in enumerate(events[:3], 1):
            print(f"\n{i}. {event.title}")
            print(f"   Time: {event.start_time}")
            print(f"   Location: {event.location_name or 'TBD'}")
            print(f"   Free: {event.is_free}")

        # Save to file
        output_dir = Path(__file__).parent.parent / "data" / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "events_eventbrite.json"

        with open(output_file, "w") as f:
            json.dump([e.model_dump(mode="json") for e in events], f, indent=2, default=str)

        print(f"\n💾 Saved {len(events)} events to {output_file}")
    else:
        print("\n❌ No events extracted")
