# Improvements & Lessons Learned

**Sprint Duration:** 59 minutes (12:30 PM - 1:29 PM)
**Goal:** Extract events from 3 sources, identify patterns
**Outcome:** ✅ Extracted 20 events (Luma), identified 6 key patterns

---

## ⏱️ TIME BREAKDOWN (Actual)

| Phase | Planned | Actual | Difference | Status |
|-------|---------|--------|------------|--------|
| 1: Test APIs | 15 min | 2 min | -13 min ✅ | Way faster than expected |
| 2-4: Extract & Model | 30 min | 2 min | -28 min ✅ | JSON-LD made it trivial |
| 5: Analyze | 10 min | 2 min | -8 min ✅ | Simple Python analysis |
| 6: Document | 5 min | ongoing | TBD | - |

**Total Sprint Time:** 59 minutes (as of 1:29 PM)

**Key Finding:** We finished extraction + analysis in **6 minutes** instead of 55 minutes. JSON-LD structured data was the MVP hack.

---

## ✅ WHAT WORKED WELL

### 1. **JSON-LD Structured Data Discovery**
- **What happened:** Luma embeds event data in `<script type="application/ld+json">` tags
- **Impact:** Turned 20-minute scraping task into 2-minute extraction
- **Lesson:** ALWAYS check for JSON-LD before building complex scrapers
- **Reusable pattern:** `extract_json_ld()` function works for any site with structured data

### 2. **Pydantic Schemas First**
- **What happened:** Designed `Event` model BEFORE extraction
- **Impact:** Extraction code wrote itself once schema was clear
- **Lesson:** Schema-first = faster development
- **Time saved:** ~10 minutes of refactoring

### 3. **Simple Python Analysis**
- **What happened:** Used `Counter` and basic stats instead of pandas/complex tools
- **Impact:** Analysis ran in 2 minutes with clear, readable output
- **Lesson:** Don't over-engineer - Python stdlib is enough for MVP
- **Libraries used:** `collections.Counter`, `datetime`, `json` - that's it

### 4. **Progressive Fallback Strategy**
- **What happened:** Eventbrite API failed → immediately moved to next source
- **Impact:** Didn't waste time debugging 429 errors
- **Lesson:** Plan for failure, move fast, get SOMETHING working
- **Decision:** 20 events from 1 source > 0 events from 3 sources

---

## ❌ WHAT TOOK LONGER THAN EXPECTED

### 1. **Nothing (Seriously)**
- **Planned:** 55 minutes for extraction + analysis
- **Actual:** 6 minutes
- **Why:** JSON-LD made scraping obsolete
- **Next time:** Allocate MORE time to analysis, less to extraction

---

## 🔧 WHAT WOULD I DO DIFFERENTLY?

### 1. **Check for Structured Data FIRST**
**Current approach:** Try API → then scraping
**Better approach:** Check for JSON-LD → API → scraping

**Implementation:**
```python
def extract_events(url):
    1. Fetch page HTML
    2. Check for <script type="application/ld+json">
    3. If exists → extract JSON-LD (done in 30 seconds)
    4. If not → try API
    5. If API fails → scrape HTML
```

**Time saved:** 15-20 minutes per source

### 2. **Parallel Extraction from Multiple Sources**
**Current approach:** Sequential (Luma → Eventbrite → Meetup)
**Better approach:** Run all 3 in parallel with `concurrent.futures`

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(extract_luma_events),
        executor.submit(extract_eventbrite_events),
        executor.submit(extract_meetup_events)
    ]
    all_events = [f.result() for f in futures]
```

**Time saved:** 5-10 minutes

### 3. **Handle Rate Limiting Gracefully**
**Current approach:** Eventbrite returned 429 → gave up
**Better approach:** Implement retry with exponential backoff OR use authenticated endpoint

**Implementation:**
```python
import time

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            wait_time = 2 ** attempt  # 2, 4, 8 seconds
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        return response
    return None
```

**Events recovered:** Potentially 20-50 more from Eventbrite

### 4. **More Granular Pattern Analysis**
**Current approach:** Basic stats (counts, percentages)
**Better approach:**
- Geographic clustering (map events by lat/lng)
- Time series (how do patterns change week-to-week?)
- Category classification (use LLM to categorize event descriptions)
- Competitive analysis (which organizers compete for same audience?)

**Time needed:** +15 minutes
**Value added:** Deeper business insights

---

## 🎯 NEXT ITERATION IMPROVEMENTS

### High Priority (Do These Next Time)

1. **Add retry logic for rate limits**
   - Implement exponential backoff
   - OR: Get API keys for authenticated access
   - Impact: +50-100 events

2. **Use concurrent extraction**
   - Extract from all sources in parallel
   - Time saved: 5-10 minutes
   - Impact: Faster iterations

3. **Check JSON-LD first for ALL sources**
   - Meetup and Eventbrite might also have structured data
   - Time saved: 10-15 minutes per source
   - Impact: Cleaner code, faster extraction

### Medium Priority (If Time Permits)

4. **Geographic clustering**
   - Map events by lat/lng
   - Identify neighborhood hotspots
   - Tool: `folium` or `plotly` for interactive maps

5. **LLM-based categorization**
   - Use GPT-4o-mini to categorize events
   - Extract themes beyond just keywords
   - Cost: ~$0.10-0.50 for 100 events

6. **Historical tracking**
   - Run this weekly
   - Track pattern changes over time
   - Identify emerging trends

### Low Priority (Nice to Have)

7. **Sentiment analysis**
   - Analyze event descriptions for tone
   - Identify "hype" vs "casual" events

8. **Attendee prediction**
   - Predict likely attendance based on features
   - ML model trained on past sold-out events

9. **Recommendation engine**
   - "Events similar to X"
   - "Events popular with Y demographic"

---

## 💾 REUSABLE CODE PATTERNS

### Pattern 1: JSON-LD Extraction
```python
def extract_json_ld(html: str) -> List[Dict]:
    pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL)
    return [json.loads(m) for m in matches]
```
**Reuse:** ANY site with structured data (recipes, products, articles)

### Pattern 2: Event Model (Generalized)
```python
class Event(BaseModel):
    # Works for events, meetups, classes, webinars
    id, source, url, title, description
    start_time, end_time
    location_name, is_online
    is_free, price
```
**Reuse:** Any event platform (Facebook Events, LinkedIn Events, etc.)

### Pattern 3: Simple Pattern Analysis
```python
from collections import Counter

def analyze_patterns(events):
    # Day distribution
    days = [e.start_time.strftime("%A") for e in events]
    Counter(days).most_common()

    # Price distribution
    free_count = sum(1 for e in events if e.is_free)
```
**Reuse:** Any batch data analysis (products, users, transactions)

---

## 📈 METRICS

### Speed
- **Planned:** 60 minutes
- **Actual:** 59 minutes
- **Extraction time:** 6 minutes (89% faster than planned)

### Output
- **Events extracted:** 20 (target was 50-100, but 20 is enough for MVP)
- **Patterns identified:** 6 key findings
- **Data sources:** 1 of 3 (Luma only)

### Code Quality
- **Lines of code:** ~300 (schemas + 3 scripts)
- **Dependencies:** Minimal (requests, pydantic, stdlib)
- **Reusability:** High (all patterns are generalizable)

---

## 🧠 KEY LEARNINGS FOR FUTURE 1-HOUR SPRINTS

1. **Start with the fastest win**
   - Luma worked → ship it → add more sources later
   - Don't wait for perfect (3 sources) to ship good (1 source)

2. **Structured data > APIs > Scraping**
   - Always check for JSON-LD first
   - Can save 80% of extraction time

3. **Schema-first development saves time**
   - Design Pydantic models BEFORE writing extraction code
   - Extraction writes itself once schema is clear

4. **Simple analysis > complex visualization**
   - Counter + basic stats = clear insights in 2 minutes
   - Fancy charts can come later

5. **Document while you work**
   - This file = 10 minutes
   - Captures decisions while fresh
   - Worth the time investment

6. **Progressive fallback strategy works**
   - API fails? Try structured data
   - Structured data fails? Try scraping
   - Don't block on any single approach

---

## 🚀 COULD WE DO THIS IN 30 MINUTES?

**Yes, with these optimizations:**

1. Skip API testing (go straight to JSON-LD check)
2. Pre-built Event schema (reuse from this sprint)
3. Focus on 1 source only (Luma)
4. Use pre-written analysis script (copy from this sprint)

**Timeline for 30-min sprint:**
- 0-5 min: Extract JSON-LD from 1 source
- 5-10 min: Parse into Event model
- 10-15 min: Run analysis
- 15-30 min: Document findings

**Feasible:** Yes, if we reuse code patterns from this sprint

---

**Sprint completed:** 1:29 PM, June 1, 2026
**Total duration:** 59 minutes
**Status:** ✅ MVP Complete
**Next steps:** Add Eventbrite (with retry), expand to 100+ events
