"""
Phase 4: Pattern Analysis

Analyze extracted events to identify trends
Time: 10-15 minutes (12:30-12:45 PM)
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas import Event, EventCollection

# Setup
DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"


def load_events() -> EventCollection:
    """Load extracted events"""
    with open(DATA_PROCESSED / "events_toronto.json", "r") as f:
        data = json.load(f)
        return EventCollection(**data)


def analyze_timing(events: List[Event]) -> Dict:
    """Analyze when events happen"""
    print("\n📅 TIMING PATTERNS")
    print("-" * 60)

    # Parse datetime strings back to datetime objects
    parsed_events = []
    for e in events:
        if isinstance(e.start_time, str):
            e.start_time = datetime.fromisoformat(e.start_time.replace("Z", "+00:00"))
        parsed_events.append(e)

    # Day of week distribution
    days = [e.start_time.strftime("%A") for e in parsed_events]
    day_counts = Counter(days)

    print("Events by day of week:")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        count = day_counts.get(day, 0)
        bar = "█" * count
        print(f"  {day:10s}: {bar} ({count})")

    # Time of day
    hours = [e.start_time.hour for e in parsed_events]
    morning = sum(1 for h in hours if 6 <= h < 12)
    afternoon = sum(1 for h in hours if 12 <= h < 17)
    evening = sum(1 for h in hours if 17 <= h < 22)
    night = sum(1 for h in hours if h >= 22 or h < 6)

    print("\nEvents by time of day:")
    print(f"  Morning (6am-12pm):   {morning}")
    print(f"  Afternoon (12pm-5pm): {afternoon}")
    print(f"  Evening (5pm-10pm):   {evening}")
    print(f"  Night (10pm-6am):     {night}")

    return {
        "day_distribution": dict(day_counts),
        "time_distribution": {
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "night": night
        }
    }


def analyze_locations(events: List[Event]) -> Dict:
    """Analyze where events happen"""
    print("\n📍 LOCATION PATTERNS")
    print("-" * 60)

    # Online vs in-person
    online = sum(1 for e in events if e.is_online)
    in_person = len(events) - online

    print(f"Event format:")
    print(f"  In-person: {in_person} ({in_person/len(events)*100:.1f}%)")
    print(f"  Online:    {online} ({online/len(events)*100:.1f}%)")

    # Location names (for in-person events)
    locations = [e.location_name for e in events if e.location_name]
    location_counts = Counter(locations)

    print(f"\nTop venues (showing up to 5):")
    for loc, count in location_counts.most_common(5):
        print(f"  {loc}: {count} event(s)")

    # Neighborhoods (if available)
    neighborhoods = [e.neighborhood for e in events if e.neighborhood]
    if neighborhoods:
        neighborhood_counts = Counter(neighborhoods)
        print(f"\nTop neighborhoods:")
        for n, count in neighborhood_counts.most_common(5):
            print(f"  {n}: {count} event(s)")

    return {
        "online_vs_inperson": {"online": online, "in_person": in_person},
        "top_venues": dict(location_counts.most_common(5))
    }


def analyze_pricing(events: List[Event]) -> Dict:
    """Analyze event pricing"""
    print("\n💰 PRICING PATTERNS")
    print("-" * 60)

    free_count = sum(1 for e in events if e.is_free)
    paid_count = len(events) - free_count

    print(f"Pricing distribution:")
    print(f"  Free:  {free_count} ({free_count/len(events)*100:.1f}%)")
    print(f"  Paid:  {paid_count} ({paid_count/len(events)*100:.1f}%)")

    # Price distribution for paid events
    paid_events = [e for e in events if not e.is_free and e.price is not None]
    if paid_events:
        prices = [e.price for e in paid_events]
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)

        print(f"\nPaid events price range:")
        print(f"  Average: ${avg_price:.2f}")
        print(f"  Range:   ${min_price:.2f} - ${max_price:.2f}")

    # Availability
    sold_out = sum(1 for e in events if e.availability and "sold" in e.availability.lower())
    if sold_out > 0:
        print(f"\nSold out events: {sold_out}")

    return {
        "free_vs_paid": {"free": free_count, "paid": paid_count},
        "price_stats": {
            "avg": avg_price if paid_events else 0,
            "min": min_price if paid_events else 0,
            "max": max_price if paid_events else 0
        } if paid_events else {}
    }


def analyze_organizers(events: List[Event]) -> Dict:
    """Analyze who's organizing events"""
    print("\n👥 ORGANIZER PATTERNS")
    print("-" * 60)

    # Organizer types
    org_types = [e.organizer_type for e in events if e.organizer_type]
    type_counts = Counter(org_types)

    print("Organizer types:")
    for org_type, count in type_counts.most_common():
        print(f"  {org_type}: {count}")

    # Top organizers
    organizers = [e.organizer_name for e in events if e.organizer_name]
    organizer_counts = Counter(organizers)

    print(f"\nMost active organizers (top 5):")
    for org, count in organizer_counts.most_common(5):
        print(f"  {org}: {count} event(s)")

    return {
        "organizer_types": dict(type_counts),
        "top_organizers": dict(organizer_counts.most_common(5))
    }


def analyze_categories(events: List[Event]) -> Dict:
    """Analyze event categories/themes"""
    print("\n🏷️  EVENT THEMES")
    print("-" * 60)

    # Extract keywords from titles
    all_words = []
    for e in events:
        words = e.title.lower().split()
        all_words.extend(words)

    # Filter common words
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "is", "are", "as", "be", "this", "that", "-", "|", "&", "s"}
    meaningful_words = [w for w in all_words if w not in stopwords and len(w) > 2]

    word_counts = Counter(meaningful_words)

    print("Most common themes (from event titles):")
    for word, count in word_counts.most_common(10):
        print(f"  {word}: {count}")

    return {
        "top_keywords": dict(word_counts.most_common(10))
    }


def main():
    print("=" * 60)
    print("PHASE 5: PATTERN ANALYSIS")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%I:%M %p')}")

    # Load events
    collection = load_events()
    events = collection.events

    print(f"\nAnalyzing {len(events)} events from {collection.city}...")

    # Run analyses
    timing = analyze_timing(events)
    locations = analyze_locations(events)
    pricing = analyze_pricing(events)
    organizers = analyze_organizers(events)
    themes = analyze_categories(events)

    # Save patterns to file
    patterns = {
        "summary": {
            "total_events": len(events),
            "sources": collection.sources,
            "city": collection.city,
            "extracted_at": collection.extracted_at
        },
        "timing": timing,
        "locations": locations,
        "pricing": pricing,
        "organizers": organizers,
        "themes": themes
    }

    output_file = Path(__file__).parent.parent / "patterns.json"
    with open(output_file, "w") as f:
        json.dump(patterns, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"💾 Patterns saved to: patterns.json")
    print(f"End time: {datetime.now().strftime('%I:%M %p')}")


if __name__ == "__main__":
    main()
