"""
Parse Eventbrite data from Apify and convert to our Event model
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event


def parse_eventbrite_apify():
    """Parse Eventbrite data from Apify scraper"""

    eventbrite_file = Path(__file__).parent.parent / "data" / "raw" / "eventbrite_june_raw.json"

    with open(eventbrite_file) as f:
        eventbrite_data = json.load(f)

    print(f"📋 Parsing {len(eventbrite_data)} Eventbrite events...")

    events = []
    for event_data in eventbrite_data:
        try:
            event_id = event_data.get("eventbriteId", event_data.get("id", ""))
            title = event_data.get("title", "Unknown Event")
            description = event_data.get("description", "")
            url = event_data.get("url", "")

            # Date parsing
            start_date = event_data.get("startDate", "")
            start_time_str = event_data.get("startTime", "00:00:00")

            if start_date:
                # Combine date and time
                if start_time_str and start_time_str != "00:00:00":
                    start_datetime_str = f"{start_date}T{start_time_str}"
                else:
                    start_datetime_str = f"{start_date}T00:00:00"

                try:
                    start_time = datetime.fromisoformat(start_datetime_str)
                except:
                    # Fallback to just date
                    start_time = datetime.fromisoformat(start_date)
            else:
                continue  # Skip events without date

            # End time
            end_date = event_data.get("endDate")
            if end_date:
                end_time_str = event_data.get("endTime", "00:00:00")
                if end_time_str and end_time_str != "00:00:00":
                    end_datetime_str = f"{end_date}T{end_time_str}"
                else:
                    end_datetime_str = f"{end_date}T00:00:00"
                try:
                    end_time = datetime.fromisoformat(end_datetime_str)
                except:
                    end_time = None
            else:
                end_time = None

            # Venue
            venue = event_data.get("venue", {})
            location_name = venue.get("name") if venue else None
            address = venue.get("streetAddress") if venue else None
            city = venue.get("city", "Toronto") if venue else "Toronto"

            latitude = float(venue.get("latitude")) if venue and venue.get("latitude") else None
            longitude = float(venue.get("longitude")) if venue and venue.get("longitude") else None

            # Pricing
            pricing = event_data.get("pricing", {})
            is_free = pricing.get("isFree", False) if pricing else False
            price = pricing.get("minPrice") if pricing and not is_free else None
            currency = pricing.get("currency") if pricing else None
            # Default to CAD if None
            if not currency:
                currency = "CAD"

            # Online/offline
            is_online = event_data.get("isOnline", False)

            # Image
            image_url = event_data.get("imageUrl")

            # Create Event
            event = Event(
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
                is_online=is_online,
                latitude=latitude,
                longitude=longitude,
                organizer_name=None,  # Not provided by this scraper
                organizer_type="Organization",
                is_free=is_free,
                price=float(price) if price else None,
                currency=currency,
                image_url=image_url,
                tags=[],
            )
            events.append(event)

        except Exception as e:
            print(f"⚠️  Error parsing event: {e}")
            continue

    print(f"✅ Successfully parsed {len(events)} events")

    # Save
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "events_eventbrite.json"

    with open(output_file, "w") as f:
        json.dump([e.model_dump(mode="json") for e in events], f, indent=2, default=str)

    print(f"💾 Saved to {output_file}")

    return events


if __name__ == "__main__":
    events = parse_eventbrite_apify()

    print(f"\n📋 Sample events:")
    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event.title}")
        print(f"   Date: {event.start_time.strftime('%B %d, %Y')}")
        print(f"   Location: {event.location_name or 'TBD'}")
        print(f"   Free: {event.is_free}")
