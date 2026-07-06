# Toronto Events Analysis

Sub-project of City Intelligence Agent analyzing event patterns in Toronto.

## Objective

Extract events from Eventbrite, Luma, and Meetup.com to identify:
- Popular event categories
- Location clusters (which neighborhoods?)
- Timing patterns (when do events happen?)
- Price distribution (free vs paid)
- Organizer types

## Data Sources

1. **Eventbrite** - Ticketing platform
2. **Luma** - Modern event platform
3. **Meetup.com** - Community meetups

## Output

- `data/processed/events_toronto.json` - Unified event data
- `patterns.md` - Analysis findings
- `improvements.md` - Lessons learned

## Usage

```bash
# Phase 1: Test APIs
python scripts/1_test_apis.py

# Phase 2: Extract all events
python scripts/2_extract_events.py

# Phase 3: Analyze patterns
python scripts/3_analyze_patterns.py
```

---

**Sprint:** 1 hour (12:30 PM - 1:30 PM, June 1, 2026)
