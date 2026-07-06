# Forno Cultura Subscription SSR Testing

Using Semantic Similarity Rating (SSR) to predict subscription intent for Forno Cultura's King Street location.

## Context Documents

**Business context and planning live in Obsidian vault:**
```
/Users/snehamehrin/Desktop/obsidian_vaults/business/Projects/Symantic Similiary Project/
├── Forno - Symantic Similarity Idea.md  # Implementation guide, personas, concepts
└── semantic similarity.pdf               # Academic paper (Maier et al., 2025)
```

**Implementation code lives here:**
```
/Users/snehamehrin/Desktop/ai_product_intelligence/forno_subscription_ssr/
```

**Why separated?**
- Obsidian vaults = context, research, documentation
- AI product intelligence = executable code, tests, deployment
- Implementation references context documents for business logic

## Method

Based on Maier et al. (2025) - "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings"

1. Generate free-text subscription intent from synthetic personas
2. Embed responses using OpenAI text-embedding-3-small
3. Compare to Likert anchor statements via cosine similarity
4. Convert to probability distribution over 1-5 rating scale

## Project Structure

```
forno_subscription_ssr/
├── prompts/          # LLM prompts as .txt files
├── src/forno_ssr/    # Core implementation
├── scripts/          # Executable scripts
├── tests/inputs/     # Sample test data
├── data/             # Survey results (gitignored)
└── logs/             # Runtime logs (gitignored)
```

## Setup

```bash
# Create virtual environment
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

## Usage

### Run Survey & Analysis (Command Line)

```bash
# Run survey
python scripts/run_survey.py

# Analyze results
python scripts/analyze_results.py

# Analyze by session type
python scripts/analyze_session_types.py
```

### Interactive Web Dashboard

View results in an interactive web dashboard:

```bash
# Launch webapp
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

**Dashboard includes:**
- 📊 Executive Summary - Top-line findings and recommendations
- 👥 Personas - 14 customer profiles with ratings
- 📍 Demographics - King Street market analysis
- 📈 Results - Interactive charts and heatmaps
- 🎯 Recommendations - Actionable next steps

## Concepts Being Tested

1. **King West Sandwich + Coffee Pass** - For lunch regulars
2. **King West Bread & Pantry Box** - For at-home consumption
3. **Underground Regulars Club** - For community/experience seekers

## Personas (14 King Street Types)

**Original 8 personas:**
- Tech worker (27, 3-4 lunches/week)
- Creative director (34, bread + sweets 2x/week)
- Design student (22, afternoon coffee + pastry)
- Couple (40, weekly bread + date night)
- Remote worker (30, daily coffee)
- Local resident (45, weekend bread)
- Fitness enthusiast (26, occasional)
- Foodie (55, quality-focused regular)

**New 6 personas (Added June 15, 2026):**
- Morning commuter (29, Financial District, 5x/week grab-and-go)
- Coffee chat professional (35, sales/BD, 2-3 meetings/week)
- Shopify worker (28, next door at King-Portland Centre, daily visitor)
- Condo resident (32, remote worker, small kitchen, frequent visitor)
- Post-work pickup (40, suburban commuter, evening bread for dinner)
- Weekend brunch visitor (26, Entertainment District destination, weekly)
