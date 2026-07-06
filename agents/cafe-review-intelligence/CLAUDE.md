# Cafe Review Intelligence Agent - Development Notes

## Project Overview

**Agent 1** from the Toronto Cafe Decode project. Analyzes Google reviews for cafes through a 5-layer behavioral framework and generates actionable experiments.

## Architecture Decisions

### 1. Pydantic-First Validation

All data flows through Pydantic schemas - this is the single source of truth.

**Why:**
- Catches bad data from Apify before it corrupts analysis
- LLM output is validated before being saved
- Type safety throughout the pipeline

**Pattern:**
```python
# Always validate LLM output
data = json.loads(llm_response)
insight = BehavioralInsight(**data)  # Pydantic validates here
```

### 2. OpenAI for Structured Output

Using `gpt-4o` with `response_format={"type": "json_object"}` ensures valid JSON responses.

**Lesson:** Claude wraps JSON in explanatory text - OpenAI's JSON mode is cleaner for this use case.

### 3. Behavioral Keywords as Configuration

Keywords are stored in `KeywordConfig` Pydantic model, not hardcoded.

**Why:**
- Easy to update without changing code
- Can A/B test different keyword sets
- User can customize for their domain

### 4. Two-Stage Analysis

1. **Deterministic keyword detection** - Fast, cheap, catches clear patterns
2. **LLM insight generation** - Expensive, smart, connects patterns to framework

**Why:**
- Keyword detection is reliable for obvious signals (e.g., "used to" = churn)
- LLM adds context and maps to framework layers
- Saves tokens by pre-filtering

## Apify Integration

### Google Maps Scraper

**Actor ID:** `compass/google-maps-scraper`

**Input format:**
```python
{
    "searchStringsArray": ["Cafe Name Toronto"],
    "maxReviews": 50,
    "reviewsSort": "newest",
    "scrapeReviewerName": True,
    ...
}
```

**Gotcha:**
- Apify returns ISO datetime strings with "Z" suffix
- Need to handle: `.replace("Z", "+00:00")` before parsing
- First result is usually the correct place, but verify cafe_name matches

## 5-Layer Framework Mapping

The framework is the core differentiator:

1. **Onboarding** - First visit friction
2. **Activation** - Getting them back in 7-10 days
3. **Retention** - Habit formation, loyalty
4. **Monetization** - ARPU, bundles, upsells
5. **Social** - Instagram-worthy, UGC, virality

**Insight Quality Rule:**
- High confidence: 10+ mentions
- Medium confidence: 5-9 mentions
- Low confidence: 3-4 mentions

Don't generate insights for <3 mentions - not statistically meaningful.

## Prompt Engineering

### System Prompt Pattern

The `insight_generator.txt` prompt:
1. Defines the framework clearly
2. Shows examples of good vs bad experiments
3. Specifies exact JSON output format
4. Emphasizes "specific, not generic" experiments

**Key instruction:**
> "Don't say 'improve customer service' - say 'Train staff to greet first-timers within 30 seconds and offer a menu explanation'"

Specificity drives actionability.

## Output Strategy: JSON Files

### Why JSON Over Database?

1. **Simplicity** - No external dependencies, no database setup
2. **Version control** - Can commit results to git
3. **Portability** - Easy to share, analyze, or migrate
4. **Transparency** - Open in any text editor
5. **Cost** - Zero infrastructure costs

### File Structure

Each analysis run creates 3 files in `data/`:
- `{cafe_name}_reviews_{timestamp}.json` - Raw reviews
- `{cafe_name}_signals_{timestamp}.json` - Detected behavioral signals
- `{cafe_name}_analysis_{timestamp}.json` - Complete framework analysis

Timestamps allow tracking changes over time (e.g., run weekly, compare).

## Lessons Learned

### 1. Apify Rate Limits

Running 30 cafes sequentially can take 30-60 minutes. Consider:
- Batch processing in smaller groups (5-10 cafes)
- Running overnight for full 30-cafe analysis
- Apify has concurrent run limits

### 2. LLM Token Costs

For 50 reviews:
- Avg 500 words per review = 25K words = 33K tokens input
- GPT-4o at $2.50/1M input tokens = ~$0.08 per cafe
- 30 cafes = ~$2.40 for full pilot analysis

**Cheap enough to run weekly.**

### 3. Keyword Detection is Powerful

70% of insights can be generated from keyword patterns alone. LLM adds:
- Context interpretation
- Framework mapping
- Experiment specificity

But the raw signals are already valuable.

### 4. Sample Size Matters

- 10 reviews: Too few for patterns
- 20-30 reviews: Patterns start to emerge
- 50+ reviews: High confidence insights
- 100+ reviews: Diminishing returns (older reviews less relevant)

**Sweet spot: 40-60 recent reviews**

## Testing Strategy

1. **Use sample reviews** in `tests/inputs/`
2. **Test each module independently** before integration
3. **Validate with known cafes** - pick 2-3 you know well, check if insights match reality
4. **Track false positives** - if LLM hallucinates insights, add to prompt as counter-examples

## Next Steps (For Future Development)

### 1. Weekly Digest Script
Batch process 10-30 cafes and generate comparative insights:
- Which issues are trending across Toronto?
- Which cafes are outliers?
- Neighborhood-level patterns

### 2. Competitor Comparison
For each cafe, track 3-5 nearby competitors:
- Review velocity changes
- Rating trends
- New insights appearing

### 3. Experiment Tracking
Add JSON output for tracking which experiments cafes actually run:
- Baseline metrics
- Experiment start/end dates
- Results
- Learnings

Could be as simple as a `{cafe_name}_experiments.json` file you manually update.

### 4. Automated Monitoring
Run weekly for same cafes, detect:
- New churn signals (quality dropping?)
- Loyalty increases (what changed?)
- Sentiment shifts

## File Organization

```
cafe-review-intelligence/
├── src/cafe_intelligence/      # Core modules
│   ├── schemas.py              # Pydantic models (single source of truth)
│   ├── apify_scraper.py        # Google Maps integration
│   ├── sentiment_analyzer.py  # Keyword detection
│   ├── insight_generator.py   # LLM analysis
│   └── json_logger.py          # JSON file output
├── scripts/                    # Executable scripts
│   └── run_single_cafe.py      # Main entry point
├── prompts/                    # LLM prompts as .txt
│   └── insight_generator.txt   # Framework mapping prompt
└── database_schema.sql         # Supabase table definitions
```

## Quick Start Commands

```bash
# Setup
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Then edit with API keys (Apify + OpenAI only)

# Analyze a cafe
python scripts/run_single_cafe.py "Quantum Coffee" "Toronto"

# Or run interactively
python scripts/run_single_cafe.py
```

## Integration with Cafe Decode Workflow

This agent feeds into the broader workflow:

1. **Field observation** (manual) - Visit cafe, take notes
2. **Review intelligence** (this agent) - Analyze what customers say
3. **Synthesis** - Combine field notes + review insights
4. **Reel creation** - Turn insights into content
5. **Consulting offer** - Use insights for paid work

**This agent automates step 2**, freeing you to focus on synthesis and content.

## Success Metrics

Track for yourself:
- **Coverage:** How many of your 30 cafes analyzed?
- **Insight quality:** Do insights match your field observations?
- **Actionability:** Could a cafe founder actually run these experiments?
- **Time savings:** Manual analysis = 2-3 hours/cafe. Agent = 5 minutes.

**Goal:** 30 cafes analyzed in <3 hours total (vs 60-90 hours manual)

---

Last updated: 2026-06-16
