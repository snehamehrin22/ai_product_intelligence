# City Intelligence Agent

Multi-city cultural & consumption intelligence platform. Analyzes demographics, trends, and consumption patterns through interdisciplinary lens (anthropology, economics, geopolitics, history) to generate actionable business insights.

## Overview

**Core Thesis:** Human behavior and consumption are changing. We analyze these changes city-by-city through multiple academic lenses to help businesses navigate with data and AI agents.

**Starting City:** Toronto (June 2026)
**Scalability:** Framework designed to expand to any city globally

## How It Works

### 4-Lens Analysis Framework

1. **Anthropology Lens**
   - Rituals and behaviors forming
   - Identity shifts and belonging patterns
   - Status symbols and community formation

2. **Economics Lens**
   - Spending power by demographic
   - Affordability vs prioritization
   - Wealth distribution and economic anxiety

3. **Geopolitics Lens**
   - Migration patterns and settlement
   - Policy impacts (housing, immigration, trade)
   - Global city dynamics

4. **History Lens**
   - Evolution patterns and cycles
   - Continuity vs rupture analysis
   - What's genuinely new vs recurring

### Business Translation

For each trend identified:
- **Opportunity:** What businesses should exist/expand?
- **Threat:** What's declining/at risk?
- **Target Demographic:** Who to serve?
- **Positioning:** How to message?
- **Timing:** Now, 6 months, 12 months?
- **Evidence Strength:** High/Medium/Low confidence

## Project Structure

```
city-intelligence/
├── prompts/                    # LLM analysis prompts (one per lens)
├── src/city_intelligence/      # Core logic
│   ├── schemas.py             # Pydantic models
│   ├── data_sources.py        # API integrations
│   ├── analyzers/             # 4-lens analyzers + synthesis
│   ├── business_translator.py # Insights → business actions
│   └── main_loop.py           # Orchestration
├── scripts/                    # Entry points
│   ├── analyze_city.py        # CLI: analyze_city.py --city toronto
│   └── generate_report.py    # Generate intelligence report
├── data/                       # City-specific data & outputs
│   ├── toronto/               # Raw Toronto data
│   ├── cache/                 # API response cache
│   └── outputs/               # Generated reports
└── tests/                      # Test data and scenarios
```

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your API keys (OpenAI, Statistics Canada, etc.)
```

## Usage

### Analyze a City

```bash
python scripts/analyze_city.py --city toronto
```

### Generate Report

```bash
python scripts/generate_report.py --city toronto --output pdf
```

## Data Sources (Toronto MVP)

**Demographics:**
- Statistics Canada (census, immigration)
- Toronto Open Data Portal
- City economic indicators

**Consumption:**
- Retail foot traffic trends
- Restaurant/cafe density
- E-commerce trends by neighborhood

**Cultural:**
- Social media trends (Twitter, Instagram)
- Google Trends (Toronto searches)
- Reddit r/toronto sentiment

**Economic:**
- Real estate prices by neighborhood
- Employment data by sector
- Business formation/closure rates

**Geopolitical:**
- Immigration statistics
- Policy changes (municipal, provincial, federal)
- Trade dynamics

## Output Example

```
Trend: "Wellness cafe culture among South Asian millennials in Scarborough"

Anthropology: Status shift from traditional tea shops to third-place wellness spaces
Economics: $40-60K household income, willing to spend $15-20 per visit
Geopolitics: Second-generation immigrants, blending identities
History: Mirrors Italian cafes in Little Italy (1960s-80s)

Business Insight:
→ Opportunity: Wellness cafes with culturally-adapted offerings
→ Target: 25-35 year old South Asian women, health-conscious
→ Location: Scarborough Town Centre area
→ Timing: NOW - early mover advantage
→ Evidence: HIGH
```

## MVP Scope (Toronto - 2 Week Sprint)

**Week 1: Data Collection & Framework**
- Set up data pipelines
- Build 4-lens analyzer prompts
- Create Pydantic schemas
- Test on 3 sample trends

**Week 2: Business Translation & Report**
- Build business insight generator
- Create report template
- Generate first Toronto Intelligence Report
- Validate with 2-3 sample businesses

**Deliverable:** Toronto Cultural Intelligence Report (June 2026)
- 10-15 trends identified
- 4-lens analysis for each
- Business recommendations with confidence scores
- Exportable to PDF/Notion/Google Sheets

## Roadmap

**Phase 1 (June 2026):** Toronto MVP
**Phase 2 (Q3 2026):** Add 2-3 Canadian cities (Vancouver, Montreal)
**Phase 3 (Q4 2026):** Expand to US cities (NYC, LA, Miami)
**Phase 4 (2027):** Global expansion + API product

## Philosophy

- **Interdisciplinary:** No single lens captures reality
- **Data-driven:** Evidence over intuition
- **Business-focused:** Insights must be actionable
- **City-specific:** Context matters, avoid generalizations
- **Scalable:** Framework works for any city globally

---

**Last updated:** June 1, 2026
**Status:** Active Development
