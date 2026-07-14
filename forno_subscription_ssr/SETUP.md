# Forno Cultura SSR - Setup Guide

This guide walks you through setting up the project environment and running your first survey.

---

## Prerequisites

- Python 3.13+ (recommended: `/usr/local/bin/python3.13`)
- OpenAI API key with access to GPT-4o and text-embedding-3-small
- Git (for version control)

---

## Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd /Users/snehamehrin/Desktop/obsidian_vaults/business/Projects/forno_subscription_ssr

# Create virtual environment
/usr/local/bin/python3.13 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify Python version
python --version  # Should show Python 3.13.x
```

---

## Step 2: Install Dependencies

```bash
# With venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages:**
- openai >= 1.12.0
- pydantic >= 2.6.0
- python-dotenv >= 1.0.0
- numpy >= 1.26.0
- pandas >= 2.2.0
- matplotlib >= 3.8.0
- seaborn >= 0.13.0
- scikit-learn >= 1.4.0
- tqdm >= 4.66.0

---

## Step 3: Configure OpenAI API Key

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add your OpenAI API key to `.env`:

```bash
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

**Security check:**
- Verify `.env` is in `.gitignore` (already included)
- NEVER commit your API key to Git

---

## Step 4: Test Setup

Run the setup validation script:

```bash
# With venv activated
python scripts/test_setup.py
```

**Expected output:**
```
=== Forno SSR Setup Validation ===

✓ Virtual environment active
✓ Python version: 3.13.x
✓ All required packages installed
✓ OpenAI API key configured
✓ OpenAI API connection successful
✓ Embedding API working
✓ Personas loaded: 8 personas
✓ Concepts loaded: 3 concepts
✓ Anchors loaded: 2 anchor sets

Setup validation complete! ✓
```

**If any checks fail:**
- Missing packages → Run `pip install -r requirements.txt`
- API key error → Check `.env` file has correct key
- Import errors → Ensure you're in project root directory

---

## Step 5: Run a Test Survey

Run a quick test with 1 persona and 1 concept:

```bash
python scripts/test_quick_survey.py
```

This generates:
- 2 synthetic responses (2 samples)
- SSR analysis with both anchor sets
- Aggregated results
- Test outputs in `data/test_*.json`

**Expected time:** ~30 seconds

**Expected API cost:** ~$0.05 USD

---

## Step 6: Run Full Survey

Once testing is successful, run the full survey:

```bash
python scripts/run_survey.py
```

This generates:
- 48 synthetic responses (8 personas × 3 concepts × 2 samples)
- SSR analysis for all combinations
- Aggregated results

**Expected time:** ~3-5 minutes

**Expected API cost:** ~$1.50-2.00 USD (text generation + embeddings)

**Outputs saved to `data/`:**
- `responses_TIMESTAMP.json` - All synthetic responses
- `ssr_results_TIMESTAMP.json` - All SSR calculations
- `aggregated_results_TIMESTAMP.json` - Averaged results
- `aggregated_results_TIMESTAMP.csv` - Spreadsheet format

---

## Step 7: Generate Analysis

Run the analysis script:

```bash
python scripts/analyze_results.py
```

This creates visualizations and insights in `data/analysis_*/`:
- `heatmap_persona_concept.png` - Subscription intent heatmap
- `concept_comparison.png` - Bar chart comparing concepts
- `distribution_by_concept.png` - Probability distributions
- `persona_profiles.png` - Individual persona preferences
- `insights_report.txt` - Text analysis with recommendations

---

## Common Issues

### "ModuleNotFoundError: No module named 'openai'"
- **Fix:** Activate venv first: `source .venv/bin/activate`
- Then: `pip install -r requirements.txt`

### "OpenAI API key not found"
- **Fix:** Create `.env` file in project root
- Add: `OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE`

### "Rate limit exceeded"
- **Fix:** Wait 60 seconds and retry
- Or: Reduce `samples_per_combo` in `run_survey.py` (line 74)

### "Invalid API key"
- **Fix:** Verify key has access to GPT-4o and embeddings
- Check at: https://platform.openai.com/api-keys

---

## Project Structure Recap

```
forno_subscription_ssr/
├── .env                    # Your API key (gitignored)
├── .gitignore              # Protects secrets
├── requirements.txt        # Dependencies
├── README.md               # Project overview
├── SETUP.md                # This file
│
├── prompts/                # LLM prompts
│   ├── persona_system.txt
│   └── subscription_question.txt
│
├── src/forno_ssr/          # Core library
│   ├── __init__.py
│   ├── schemas.py          # Data models
│   ├── personas.py         # 8 King Street personas
│   ├── concepts.py         # 3 subscription concepts
│   ├── anchors.py          # Likert scale anchors
│   ├── llm_client.py       # OpenAI API client
│   └── ssr_engine.py       # SSR algorithm
│
├── scripts/                # Executable scripts
│   ├── test_setup.py       # Setup validation
│   ├── test_quick_survey.py # Quick test
│   ├── run_survey.py       # Full survey
│   └── analyze_results.py  # Generate visualizations
│
└── data/                   # Results (gitignored)
    └── analysis_*/         # Analysis outputs
```

---

## Next Steps

After running the full survey and analysis:

1. Review `insights_report.txt` for recommendations
2. Examine visualizations to identify winning concept
3. Decide which subscription to pilot at King Street
4. Set up KPIs for 3-month pilot test

---

## Cost Estimates

**Full survey (8 personas × 3 concepts × 2 samples):**
- Text generation: ~48 requests @ ~150 tokens each = ~$0.60
- Embeddings: ~58 texts (48 responses + 10 anchors) @ 1536 dims = ~$0.01
- **Total:** ~$0.60-1.00 USD per full survey run

**Development/testing:**
- Budget: $5-10 USD for initial testing and iteration
- Full survey can be run 10-15 times for this budget

---

## Support

**Issues?**
- Check `data/` for error logs
- Verify all setup steps completed
- Review `test_setup.py` output for diagnostics

**Customization:**
- Modify personas in `src/forno_ssr/personas.py`
- Adjust concepts in `src/forno_ssr/concepts.py`
- Tune anchors in `src/forno_ssr/anchors.py`
- Edit prompts in `prompts/`

---

**Ready to ship!** 🚀
