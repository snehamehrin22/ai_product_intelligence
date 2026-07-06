# CLAUDE.md - City Intelligence Agent

Agent-specific development guidelines and patterns.

## Project Philosophy

**Core Thesis:** Human behavior and consumption are changing. We analyze these changes city-by-city through multiple academic lenses (anthropology, economics, geopolitics, history) to help businesses navigate with data and AI agents.

**Key Principle:** NO single lens captures reality. Only multi-lens synthesis reveals actionable truth.

## Development Workflow

### 1. Adding a New City

```bash
# Create city data directory
mkdir -p data/{city_name}

# Add city metadata
# Edit src/city_intelligence/data_sources.py
# Add city-specific data sources

# Test with sample trend
python scripts/analyze_city.py --city {city_name} --trend "sample-trend"
```

### 2. Adding a New Analyzer Lens

If you need to add a 5th lens (e.g., "Technology Lens"):

1. Create prompt: `prompts/technology_lens.txt`
2. Add schema: Update `schemas.py` with `TechnologyAnalysis` model
3. Create analyzer: `src/city_intelligence/analyzers/technology.py`
4. Update synthesis: Include new lens in `analyzers/synthesis.py`
5. Update `MultiLensAnalysis` model to include new field

**Pattern:** One prompt file = one analyzer module = one Pydantic model

### 3. Testing New Trends

Always test with at least 3 scenarios:
1. **Strong signal** - High confidence, clear data
2. **Weak signal** - Emerging, ambiguous data
3. **False positive** - Noise that looks like signal but isn't

Store test cases in `tests/inputs/test_scenarios/`

## Prompt Engineering Patterns

### For Lens Analyzers

**Structure:**
```
1. Role definition (who are you?)
2. Task description (what are you analyzing?)
3. Framework (how to analyze?)
4. Output requirements (what format?)
5. Guidelines (quality standards)
6. Example (reference, not template)
```

**Key Guidelines:**
- Evidence-based (ground in data)
- Mechanism-focused (WHY not just WHAT)
- Comparative (reference other contexts)
- Nuanced (avoid oversimplification)
- Actionable (businesses must be able to use this)

### For Business Translation

Focus on:
- Opportunity identification (what should exist?)
- Threat detection (what's at risk?)
- Target demographic (who to serve?)
- Positioning (how to message?)
- Timing (when to act?)
- Evidence strength (how confident?)

## Data Source Integration

### Adding a New Data Source

1. Create API wrapper in `src/city_intelligence/data_sources.py`
2. Add authentication to `.env`
3. Implement caching (save to `data/cache/`)
4. Add to `DataSource` tracking in schemas
5. Document reliability level

### Data Quality Standards

**High reliability:**
- Government census data
- Official economic indicators
- Verified business registrations

**Medium reliability:**
- Social media aggregates
- Third-party research reports
- Crowdsourced data

**Low reliability:**
- Anecdotal observations
- Small sample surveys
- Unverified scraping

## Token Usage & Cost Management

**Lens analyzers are expensive.** Each 4-lens analysis costs ~$0.50-1.00.

**Optimization strategies:**
1. Cache intermediate results
2. Use GPT-4o-mini for drafts, GPT-4o for final
3. Batch similar trends together
4. Only regenerate when data changes significantly

**Track costs:** Log tokens used per analysis in `data/outputs/cost_log.csv`

## Common Patterns

### Pattern: Trend Identification

```python
# Don't manually list trends - discover them from data
# Use clustering, frequency analysis, LLM extraction

# Bad (manual):
trends = ["wellness cafes", "co-working spaces"]

# Good (data-driven):
trends = discover_trends_from_sources(
    social_media_data,
    business_formation_data,
    search_trends
)
```

### Pattern: Multi-lens Synthesis

```python
# Synthesis should CONNECT lenses, not just concatenate

# Bad:
synthesis = f"{anthropology} {economics} {geopolitics} {history}"

# Good:
synthesis = synthesize_lenses(
    anthropology_shows="identity shift",
    economics_shows="spending capacity",
    geopolitics_explains="why now",
    history_provides="context for cyclicality"
)
```

### Pattern: Business Insight Generation

```python
# Always provide: opportunity, threat, target, timing, evidence

# Bad:
insight = "Wellness cafes are popular"

# Good:
insight = BusinessInsight(
    opportunity="Open wellness cafe in Scarborough",
    target="25-35 South Asian women",
    timing="immediate",
    evidence_strength="high",
    reasoning="3 data sources confirm, historical parallel strong"
)
```

## Gotchas & Lessons Learned

### 1. Don't Over-Engineer Data Collection

Start simple:
- Use free/accessible data sources first
- Add paid APIs only when necessary
- Manual data collection is fine for MVP

### 2. Prompts Need City Context

Generic prompts produce generic analysis. Always inject:
- City demographics
- City history
- Current city context (policy, economy, events)

### 3. Synthesis is the Hardest Part

Connecting 4 lenses requires:
- Understanding causal relationships
- Identifying contradictions
- Weighing evidence
- Avoiding pet theories

**Solution:** Use structured synthesis prompt with explicit connection requirements.

### 4. Business Insights ≠ Academic Analysis

Businesses need:
- WHO to target (specific)
- WHERE to operate (neighborhoods, not city-wide)
- WHEN to act (now vs 6 months)
- HOW MUCH confidence (high/med/low)

Academic lens → translate to business action

## File Organization

```
city-intelligence/
├── prompts/              # One file per lens + synthesis + business
├── src/
│   ├── schemas.py       # SINGLE source of truth for data structure
│   ├── data_sources.py  # API wrappers, caching
│   ├── analyzers/       # One module per lens
│   │   ├── anthropology.py
│   │   ├── economics.py
│   │   ├── geopolitics.py
│   │   ├── history.py
│   │   └── synthesis.py
│   ├── business_translator.py
│   └── main_loop.py     # Orchestration
├── scripts/
│   ├── analyze_city.py  # Main CLI
│   └── generate_report.py
├── data/
│   ├── {city}/          # Raw data per city
│   ├── cache/           # API response cache
│   └── outputs/         # Generated reports
└── tests/
    └── inputs/          # Test scenarios
```

## Future Improvements

**Phase 2 (After Toronto MVP):**
- Comparative city analysis (Toronto vs Vancouver)
- Trend prediction (where is this going?)
- Network effects (how trends spread city-to-city)

**Phase 3 (API Product):**
- Real-time trend monitoring
- Alert system for businesses
- Custom industry filters (retail, F&B, tech)

---

**Last updated:** June 1, 2026
**Status:** Initial setup complete, building analysis pipeline
