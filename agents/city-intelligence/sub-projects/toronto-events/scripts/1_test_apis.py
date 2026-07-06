"""
Phase 1: Test APIs and get sample data

Goal: Test each API, save 3-5 sample events
Time: 15 minutes (12:30-12:45 PM)

Strategy:
- Try official APIs first
- If auth takes >5 min, switch to scraping
- Save raw samples to data/raw/
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# Setup
DATA_RAW = Path(__file__).parent.parent / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)


def test_eventbrite():
    """Test Eventbrite API or scraping"""
    print("\n🎫 Testing Eventbrite...")

    # Try public search endpoint first (no auth needed)
    # https://www.eventbrite.com/d/canada--toronto/events/

    try:
        # Option 1: Use public API endpoint if available
        # For now, let's try the search page and see structure

        url = "https://www.eventbrite.com/api/v3/destination/search/"
        params = {
            "location.address": "Toronto, ON, Canada",
            "page_size": 5,
            "expand": "venue,organizer"
        }

        # Note: This might require authentication
        # If it fails, we'll scrape the public page

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            with open(DATA_RAW / "eventbrite_sample.json", "w") as f:
                json.dump(data, f, indent=2)

            events = data.get("events", [])
            print(f"✅ Retrieved {len(events)} events from Eventbrite")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            print("💡 Trying alternative approach...")

            # Fallback: Scrape public events page
            # For MVP, we'll note this and move to next source
            print("📝 Note: Would scrape public page in production")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Recommendation: Use web scraping for Eventbrite")
        return False


def test_luma():
    """Test Luma (lu.ma) API or scraping"""
    print("\n🌟 Testing Luma...")

    # Luma likely doesn't have public API
    # We'll check their public calendar page

    try:
        # Try to fetch their Toronto calendar
        url = "https://lu.ma/toronto"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print(f"✅ Can access Luma Toronto page")
            print("📝 Note: Would scrape event data from HTML")

            # For MVP: Save page HTML as sample
            with open(DATA_RAW / "luma_page.html", "w") as f:
                f.write(response.text[:5000])  # Save first 5000 chars

            print("💡 Recommendation: Use BeautifulSoup to parse event cards")
            return False  # Scraping needed
        else:
            print(f"⚠️  Cannot access Luma page (status {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_meetup():
    """Test Meetup.com API or scraping"""
    print("\n👥 Testing Meetup.com...")

    # Meetup has GraphQL API but requires OAuth
    # Let's try their public search page

    try:
        # Try to access public events page
        url = "https://www.meetup.com/find/?location=ca--on--toronto&source=EVENTS"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print(f"✅ Can access Meetup Toronto page")
            print("📝 Note: Would scrape event data from HTML")

            # For MVP: Save page HTML as sample
            with open(DATA_RAW / "meetup_page.html", "w") as f:
                f.write(response.text[:5000])  # Save first 5000 chars

            print("💡 Recommendation: Use BeautifulSoup to parse event listings")
            return False  # Scraping needed
        else:
            print(f"⚠️  Cannot access Meetup page (status {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("PHASE 1: API Testing")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%I:%M %p')}")

    results = {
        "eventbrite": test_eventbrite(),
        "luma": test_luma(),
        "meetup": test_meetup()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for source, success in results.items():
        status = "✅ API works" if success else "🔧 Needs scraping"
        print(f"{source.title()}: {status}")

    print(f"\nEnd time: {datetime.now().strftime('%I:%M %p')}")
    print("\n📋 Next Step: Design Event model based on what we found")
    print("⏱️  Time remaining: ~45 minutes")


if __name__ == "__main__":
    main()
