# Cafe Review Intelligence Agent

**Agent 1** from the Toronto Cafe Decode project. Monitors Google reviews for Toronto cafes, analyzes them through a 5-layer behavioral framework, and outputs actionable experiments cafe founders can run.

## What It Does

1. **Scrapes Google reviews** using Apify Google Maps scraper
2. **Flags retention signals:**
   - Loyalty language: "my spot", "regular", "always", staff names
   - Churn language: "used to", "not anymore", "inconsistent", "went downhill"
   - First-timer signals: "first time", "confusing", "didn't know"
   - Repeat signals: "came back", "second visit", "within a week"
3. **Maps findings to behavioral framework:**
   - Onboarding (first visit experience)
   - Activation (getting them back within 7-10 days)
   - Retention (habit loops, loyalty)
   - Monetization (ARPU, pricing, bundles)
   - Social mechanics (Instagram-worthy, UGC)
4. **Generates actionable experiments** tied to specific review patterns
5. **Saves results as JSON files** for easy analysis and version control

## Installation

```bash
# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Analyze a single cafe
```bash
python scripts/run_single_cafe.py "Quantum Coffee" "Toronto"
```

### Weekly digest for multiple cafes
```bash
python scripts/run_weekly_digest.py
```

## Project Structure

```
cafe-review-intelligence/
├── src/cafe_intelligence/
│   ├── schemas.py              # Pydantic models
│   ├── apify_scraper.py        # Google Maps scraper
│   ├── sentiment_analyzer.py  # Behavioral keyword detection
│   ├── insight_generator.py   # Framework mapping + experiments
│   └── json_logger.py          # JSON file output
├── scripts/
│   ├── run_single_cafe.py     # Test single cafe
│   └── run_weekly_digest.py   # Batch processor
├── prompts/
│   ├── sentiment_classifier.txt
│   └── insight_generator.txt
└── tests/
    └── inputs/                 # Sample reviews
```

## Behavioral Framework

The agent maps review patterns to these growth tactics:

### 1. Onboarding
- Issues: "confusing menu", "didn't know how to order", "overwhelming"
- Experiments: Clear signage, staff greeting protocol, "first week pass"

### 2. Activation
- Signals: "came back within X days", voucher mentions, loyalty program
- Experiments: 7-day return voucher, off-peak stamped loyalty

### 3. Retention
- Loyalty: Staff names, "my spot", "always come here", "regular"
- Churn: "used to", "not anymore", "inconsistent quality"
- Experiments: Named drinks, weekly events, membership

### 4. Monetization
- Mentions: Pricing complaints/praise, "expensive but worth it", bundles
- Experiments: Coffee + pastry bundles, subscription, upsell scripts

### 5. Social Mechanics
- Signals: "Instagram-worthy", "perfect for photos", aesthetic mentions
- Experiments: Distinctive visual element, behind-the-scenes content, UGC encouragement

## Output Format

For each cafe, you get:

1. **Review summary** (count, avg rating, date range)
2. **Retention signals** (flagged keywords by type)
3. **Top 3 behavioral findings** mapped to framework
4. **Recommended experiments** (specific, actionable)
5. **Sample review excerpts** as evidence

## Output Format

Results are saved as JSON files in the `data/` directory:

### `{cafe_name}_reviews_{timestamp}.json`
- All scraped reviews with ratings, text, dates
- Average rating and total review count
- Date range of reviews

### `{cafe_name}_signals_{timestamp}.json`
- Detected behavioral signals grouped by type
- Keywords found and sample excerpts
- Signal counts per type

### `{cafe_name}_analysis_{timestamp}.json`
- Complete framework analysis
- Top 3 priority findings
- Insights grouped by framework layer
- Recommended experiments with expected impacts

## Development

Built following standard agent structure from ai_product_intelligence project.

See: `/Users/snehamehrin/Desktop/ai_product_intelligence/agents/README.md`
