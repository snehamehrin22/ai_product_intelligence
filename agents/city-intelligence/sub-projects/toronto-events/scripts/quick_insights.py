"""
Quick insights from all 83 Toronto events
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Load data
data_file = Path(__file__).parent.parent / "data" / "processed" / "events_all_sources.json"
with open(data_file) as f:
    data = json.load(f)

events = data["events"]

print("=" * 60)
print("TORONTO EVENTS QUICK INSIGHTS (83 events)")
print("=" * 60)

# 1. Free vs Paid
free_count = sum(1 for e in events if e["is_free"])
paid_count = len(events) - free_count
print(f"\n💰 PRICING")
print(f"   Free: {free_count} ({free_count/len(events)*100:.0f}%)")
print(f"   Paid: {paid_count} ({paid_count/len(events)*100:.0f}%)")

# 2. By source
print(f"\n📊 BY SOURCE")
sources = Counter(e["source"] for e in events)
for source, count in sources.most_common():
    print(f"   {source.title()}: {count} ({count/len(events)*100:.0f}%)")

# 3. Day of week patterns
days = []
for e in events:
    try:
        dt = datetime.fromisoformat(e["start_time"].replace("Z", "+00:00"))
        days.append(dt.strftime("%A"))
    except:
        continue

day_counts = Counter(days)
print(f"\n📅 MOST POPULAR DAYS")
for day, count in day_counts.most_common(3):
    print(f"   {day}: {count} events")

# 4. Time of day
hours = []
for e in events:
    try:
        dt = datetime.fromisoformat(e["start_time"].replace("Z", "+00:00"))
        hours.append(dt.hour)
    except:
        continue

# Group into time periods
morning = sum(1 for h in hours if 6 <= h < 12)
afternoon = sum(1 for h in hours if 12 <= h < 17)
evening = sum(1 for h in hours if 17 <= h < 22)
night = sum(1 for h in hours if h >= 22 or h < 6)

print(f"\n⏰ TIME OF DAY")
print(f"   Morning (6am-12pm): {morning} events")
print(f"   Afternoon (12pm-5pm): {afternoon} events")
print(f"   Evening (5pm-10pm): {evening} events")
print(f"   Night (10pm-6am): {night} events")

# 5. Top organizers
organizers = [e["organizer_name"] for e in events if e.get("organizer_name")]
org_counts = Counter(organizers)
print(f"\n🏢 TOP ORGANIZERS")
for org, count in org_counts.most_common(5):
    print(f"   {org}: {count} events")

# 6. Event categories (from title keywords)
keywords = []
for e in events:
    title = e["title"].lower()
    # Extract category hints
    if any(word in title for word in ["climate", "sustainability", "green", "carbon", "net zero"]):
        keywords.append("Climate/Sustainability")
    elif any(word in title for word in ["tech", "ai", "code", "python", "devops", "aws", "developer"]):
        keywords.append("Tech/Developer")
    elif any(word in title for word in ["music", "concert", "party", "dance", "dj"]):
        keywords.append("Music/Entertainment")
    elif any(word in title for word in ["networking", "meetup", "community"]):
        keywords.append("Networking/Community")
    elif any(word in title for word in ["game", "gaming", "card"]):
        keywords.append("Gaming")
    elif any(word in title for word in ["food", "cafe", "coffee", "restaurant"]):
        keywords.append("Food/Beverage")

keyword_counts = Counter(keywords)
print(f"\n🏷️  EVENT CATEGORIES (from titles)")
for keyword, count in keyword_counts.most_common():
    print(f"   {keyword}: {count} events")

# 7. Online vs In-person
online_count = sum(1 for e in events if e.get("is_online"))
inperson_count = len(events) - online_count
print(f"\n🌐 ONLINE VS IN-PERSON")
print(f"   In-Person: {inperson_count} ({inperson_count/len(events)*100:.0f}%)")
print(f"   Online: {online_count} ({online_count/len(events)*100:.0f}%)")

# 8. June vs July/August
june_events = []
july_events = []
august_events = []
for e in events:
    try:
        dt = datetime.fromisoformat(e["start_time"].replace("Z", "+00:00"))
        if dt.month == 6:
            june_events.append(e)
        elif dt.month == 7:
            july_events.append(e)
        elif dt.month == 8:
            august_events.append(e)
    except:
        continue

print(f"\n📆 BY MONTH")
print(f"   June: {len(june_events)} events")
print(f"   July: {len(july_events)} events")
print(f"   August: {len(august_events)} events")

# 9. Hottest week
week_counts = {}
for e in events:
    try:
        dt = datetime.fromisoformat(e["start_time"].replace("Z", "+00:00"))
        week_key = f"Week of {dt.strftime('%B %d')}"
        week_counts[week_key] = week_counts.get(week_key, 0) + 1
    except:
        continue

sorted_weeks = sorted(week_counts.items(), key=lambda x: x[1], reverse=True)
print(f"\n🔥 BUSIEST WEEKS")
for week, count in sorted_weeks[:3]:
    print(f"   {week}: {count} events")

print("\n" + "=" * 60)
