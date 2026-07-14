# Toronto Events Analysis - 1 Hour Sprint

**Start Time:** 12:30 PM
**End Time:** 1:30 PM
**Goal:** Extract events from 3 sources, identify patterns

## Timeline

| Phase | Time | Duration | Tasks |
|-------|------|----------|-------|
| 1 | 12:30-12:45 | 15 min | Test APIs, get samples |
| 2 | 12:45-12:55 | 10 min | Design Event model |
| 3 | 12:55-1:15 | 20 min | Extract all events |
| 4 | 1:15-1:25 | 10 min | Analyze patterns |
| 5 | 1:25-1:30 | 5 min | Document learnings |

## Data Sources

1. **Eventbrite** - REST API (requires OAuth/key)
2. **Luma (lu.ma)** - Check for API, fallback to scraping
3. **Meetup.com** - REST API (OAuth complex, might scrape)

## Strategy

- If API auth takes >5 min → switch to scraping
- Target: 50-100 events per source
- Identify 5-7 patterns minimum

## Success Metrics

- ✅ 150+ events extracted
- ✅ 5+ patterns identified
- ✅ Completed in 60 minutes

---

**Execution Log:**

- 12:30 PM - Project structure created
- [Time] - [What happened]
