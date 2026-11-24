# Instagram Hook Analyzer

Extracts viral Instagram Reels from creators and analyzes their hooks using AI.

## What It Does

1. **Scrapes viral Instagram Reels** from specified creators using Apify
2. **Downloads videos** and extracts hooks (first 0-5 seconds)
3. **Transcribes audio** using OpenAI Whisper
4. **Extracts on-screen text** using OCR (Tesseract)
5. **Analyzes hooks** with GPT-4o (pattern detection, scoring, insights)
6. **Outputs CSV** with hook library for content research

## Setup

### 1. Create Virtual Environment

```bash
cd instagram_hook_analyzer
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 4. Configure API Keys

Secrets live in Infisical (`APIFY_API_KEY`, `OPENAI_API_KEY`). Log in once, then run every command through `infisical run --`:

```bash
infisical login
infisical init   # links the repo to the project
infisical run -- python test_api_keys.py
```

No `.env` file is needed. `.env.example` is kept only as a list of required variable names.

Get API keys:
- Apify: https://console.apify.com/account/integrations
- OpenAI: https://platform.openai.com/api-keys

## Usage

### Quick Start

```bash
infisical run -- python scripts/analyze_creators.py
```

This will:
- Prompt for Instagram usernames
- Fetch their top viral reels
- Extract and analyze hooks
- Save results to `output/hooks_analysis.csv`

### Custom Analysis

```python
from src.instagram_hook_analyzer import HookAnalyzer

analyzer = HookAnalyzer()

# Analyze specific creators
results = analyzer.analyze_creators(
    usernames=["creator1", "creator2"],
    max_reels_per_creator=10
)

# Results include:
# - hook_text
# - hook_pattern (curiosity_gap, bold_claim, question, etc.)
# - hook_score (0-100)
# - engagement metrics
# - what_works / what_fails
```

## Output Format

CSV with columns:
- `creator_username`
- `reel_url`
- `hook_text` (combined OCR + transcript)
- `hook_pattern` (AI-classified)
- `hook_score` (0-100)
- `views`, `likes`, `comments`
- `what_works` (analysis)
- `what_fails` (analysis)
- `suggested_rewrite`
- `posted_date`

## Cost Estimate

- Apify: $0.0018 per reel
- OpenAI Whisper API: $0.006 per minute of audio
- GPT-4o: ~$0.01 per reel

**Total: ~$0.02 per reel analyzed**

## Project Structure

```
instagram_hook_analyzer/
├── .env.example            # Required variable names (secrets live in Infisical)
├── requirements.txt
├── README.md
├── src/
│   └── instagram_hook_analyzer/
│       ├── __init__.py
│       ├── scraper.py      # Apify Instagram scraper
│       ├── video_processor.py  # Download + extract hooks
│       ├── hook_analyzer.py    # GPT-4o analysis
│       └── main.py         # Orchestration
├── scripts/
│   └── analyze_creators.py # Main entry point
└── output/                 # Results (gitignored)
```
