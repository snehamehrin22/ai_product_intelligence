# Research Agent

A simple research agent that investigates observations using Perplexity Sonar API via OpenRouter.

## Setup

1. **Create virtual environment:**
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

Edit `.env` and add your API keys:
```bash
OPENROUTER_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```

## Usage

### Research from text:
```bash
python scripts/research.py --text "People are frustrated with AI tools feeling 'samey'"
```

### Research from Supabase observation:
```bash
python scripts/research.py --id T042
```

## Project Structure

```
research_agent/
├── .env                          # API keys (gitignored)
├── requirements.txt
├── prompts/
│   └── research_prompt.txt       # Perplexity query template
├── src/
│   └── research_agent/
│       ├── schemas.py            # Pydantic models
│       ├── tools_perplexity.py   # Perplexity API integration
│       ├── tools_supabase.py     # Supabase integration
│       └── utils.py              # Helper functions
└── scripts/
    └── research.py               # Main CLI script
```

## How It Works

1. Takes an observation (text or Supabase ID)
2. Loads research prompt template
3. Calls Perplexity Sonar via OpenRouter
4. Returns structured findings with sources
