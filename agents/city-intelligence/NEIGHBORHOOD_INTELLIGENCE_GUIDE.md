# Neighborhood Intelligence Guide

## Overview

The Neighborhood Intelligence analyzer conducts deep, 15-section analysis of neighborhoods to understand them as living systems. This goes far beyond demographics or business listings—it analyzes identity, culture, economics, human behavior, and strategic opportunities.

## What Gets Analyzed (15 Sections)

1. **Neighborhood Identity** - How the neighborhood sees itself and is seen by others
2. **Historical Evolution** - How it became what it is today
3. **Demographics** - Who lives here and how it's changing
4. **Economic Landscape** - Financial forces shaping business viability
5. **Business Ecosystem** - How businesses cluster, compete, and reinforce
6. **Human Movement** - Foot traffic patterns by time and day
7. **Third Place Analysis** - Ray Oldenburg's framework for community spaces
8. **Behavioral Patterns** - Recurring rituals and routines
9. **Cultural Signals** - Values expressed through the neighborhood
10. **Macro Trends** - Broader forces reshaping the area
11. **Neighborhood Needs** - Unmet needs ranked by evidence
12. **Future Outlook** - 3/5/10 year projections
13. **Café Implications** - Specific café strategy recommendations
14. **Strategic Insights** - Non-obvious insights for entrepreneurs
15. **Executive Summary** - Synthesis and one-sentence neighborhood summary

## Usage

### Basic Usage

```bash
python scripts/analyze_neighborhood.py \
  --neighborhood "King Street West" \
  --city "Toronto"
```

### With Custom Output

```bash
python scripts/analyze_neighborhood.py \
  --neighborhood "King Street West" \
  --city "Toronto" \
  --country "Canada" \
  --output json,markdown
```

### Output Formats

- `json` - Machine-readable JSON report
- `markdown` - Human-readable markdown report

Both formats include all 15 sections.

## Output Files

Reports are saved to `data/` directory:

- `king_street_west_intelligence_TIMESTAMP.json`
- `king_street_west_intelligence_TIMESTAMP.md`

## Cost & Performance

**Estimated per-neighborhood:**
- **Tokens:** ~40,000-60,000 tokens
- **Cost:** $0.50-1.00 USD
- **Time:** 5-10 minutes
- **Sections:** 15 complete analyses

**Why it costs this:**
- 15 separate LLM calls (one per section)
- Uses GPT-4o for quality and structured output
- Each prompt includes detailed instructions and frameworks
- Synthesis sections receive context from prior analyses

## Requirements

### API Keys

Set in `.env` file:

```bash
OPENAI_API_KEY=sk-...
GOOGLE_PLACES_API_KEY=...  # Optional, for business data
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `openai`
- `pydantic`
- `rich`
- `python-dotenv`
- `requests`

## How It Works

### 1. Prompt Loading

Each section has a specialized prompt in `prompts/`:
- `neighborhood_identity.txt`
- `historical_evolution.txt`
- `demographic_analysis.txt`
- etc.

### 2. LLM Analysis

Each prompt:
- Defines the analyst role (sociologist, economist, historian, etc.)
- Specifies research sources to use
- Provides analysis framework
- Requires evidence vs interpretation distinction
- Mandates "So what does this mean for a café operator?" conclusion

### 3. Pydantic Validation

All LLM responses validated against schemas in `schemas.py`:
- Ensures required fields present
- Validates data types
- Catches malformed responses
- Provides autocomplete in code

### 4. Synthesis

Final sections (13-15) receive context from all previous sections:
- Café implications synthesize all insights
- Strategic insights surface non-obvious patterns
- Executive summary tells the neighborhood story

## Validation Checklist

Before running on real data, validate:

- [ ] `.env` file has `OPENAI_API_KEY`
- [ ] `prompts/` directory has all 15 prompt files
- [ ] `schemas.py` has all 15 Pydantic models
- [ ] Script is executable (`chmod +x scripts/analyze_neighborhood.py`)
- [ ] Output directory `data/` exists or can be created

## Testing

### Dry Run (No API Cost)

```bash
# Validate setup
python -c "from city_intelligence.analyzers.neighborhood_intelligence import NeighborhoodIntelligenceAnalyzer; print('Setup valid!')"
```

### Full Test (Costs $0.50-1.00)

```bash
python scripts/analyze_neighborhood.py \
  --neighborhood "King Street West" \
  --city "Toronto"
```

**Expected output:**
- 15 section analyses printed to console
- JSON file saved to `data/`
- Markdown file saved to `data/`
- Token usage and cost summary displayed

## Example Output Structure

```json
{
  "neighborhood_name": "King Street West",
  "city": {
    "name": "Toronto",
    "country": "Canada"
  },
  "identity": {
    "known_for": "...",
    "resident_description": "...",
    "cafe_implications": "So what does this mean for a café operator? ..."
  },
  "historical_evolution": { ... },
  "demographics": { ... },
  ...
  "neighborhood_story": "A post-industrial corridor in mid-gentrification...",
  "one_sentence_summary": "..."
}
```

## Customization

### Adding a New Section

1. Create prompt file: `prompts/new_section.txt`
2. Add Pydantic model to `schemas.py`
3. Add analyzer method in `neighborhood_intelligence.py`
4. Update `run_full_analysis()` to call new method
5. Add to `NeighborhoodIntelligenceReport` model

### Modifying Prompts

Edit any file in `prompts/` directory. No code changes needed.

### Changing LLM Model

In `neighborhood_intelligence.py`, modify:

```python
model="gpt-4o"  # Change to gpt-4o-mini, gpt-4, etc.
```

**Cost implications:**
- `gpt-4o-mini`: ~$0.10/neighborhood (faster, lower quality)
- `gpt-4o`: ~$0.50/neighborhood (balanced)
- `gpt-4-turbo`: ~$1.00/neighborhood (slower, higher quality)

## Data Sources Integration

The analyzer can pull data from:

- **Statistics Canada** - Census data
- **Google Places API** - Business listings
- **Reddit API** - Community discussions
- **Toronto Open Data** - Municipal data
- **Transit Data** - TTC routes, ridership
- **Real Estate APIs** - Rent and sale prices

See `data_sources.py` for integration details.

## Troubleshooting

### "OPENAI_API_KEY not found"

Create `.env` file in project root:

```bash
OPENAI_API_KEY=sk-...
```

### "Prompt file not found"

Ensure all 15 prompt files exist in `prompts/`:

```bash
ls prompts/*.txt | wc -l  # Should show 15
```

### "Validation error"

LLM output didn't match expected schema. Check:
- Is prompt clear about required JSON structure?
- Is LLM returning all required fields?
- Check `schemas.py` for field requirements

### "Rate limit exceeded"

OpenAI API rate limit hit. Solutions:
- Add delays between sections
- Use lower tier model
- Upgrade OpenAI account tier

## Best Practices

### 1. Use for high-value decisions

This analysis costs $0.50-1.00. Use it when:
- Signing a commercial lease
- Choosing business location
- Understanding competitive landscape
- Validating market opportunity

### 2. Supplement with primary research

The analysis uses available data and AI synthesis. Always:
- Walk the neighborhood yourself
- Talk to local business owners
- Observe foot traffic patterns
- Validate AI insights with reality

### 3. Update regularly

Neighborhoods change. Re-run analysis:
- Annually for stable neighborhoods
- Quarterly for rapidly changing areas
- Before major business decisions

### 4. Compare neighborhoods

Run analysis on multiple locations to compare:
- Which has better foot traffic?
- Which values align with your brand?
- Which has fewer competitors?
- Which has better unit economics?

## Future Enhancements

Potential improvements:

- **Automated data fetching** - Pull census, business, transit data automatically
- **Comparative analysis** - Compare multiple neighborhoods side-by-side
- **Temporal analysis** - Track neighborhood changes over time
- **Visual outputs** - Maps, charts, infographics
- **API endpoint** - Serve analyses via REST API
- **Real-time updates** - Monitor neighborhood changes continuously

## Credits

Built on frameworks from:
- **Jane Jacobs** - Urban vitality and neighborhood dynamics
- **Ray Oldenburg** - Third place theory
- **Richard Florida** - Creative class and urban economics
- **Jan Gehl** - Human-centered urban design

---

**Last Updated:** 2026-06-26
**Version:** 1.0
**Status:** Production Ready
