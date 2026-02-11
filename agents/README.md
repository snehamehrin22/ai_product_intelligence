# AI Agents

This folder contains all AI agents built for various use cases.

## Agents

### 1. triage-agent
**Purpose:** Automatic journal classification system
- Processes Notion journal entries
- Splits text into cognitive blocks
- Classifies blocks by emotion, themes, behavioral patterns
- Stores results in Supabase

**Tech:** OpenAI, Notion API, Supabase, Pydantic

---

### 2. reddit_sentiment_analyzer
**Purpose:** Brand sentiment analysis from Reddit
- Scrapes Reddit posts/comments about brands
- Analyzes sentiment and trends
- Generates insights for brand monitoring

**Tech:** Reddit API, sentiment analysis

---

### 3. carousel-generator
**Purpose:** Content creation pipeline for carousels
- Transforms product research into LinkedIn/Instagram carousels
- Two-stage AI generation (Claude for patterns, ChatGPT for prose)
- Based on content pillars and voice profiles

**Tech:** Claude, ChatGPT, content generation

---

### 4. app-analyzer
**Purpose:** Deep app case studies
- Analyzes apps with bi-directional Knowledge Brain connection
- Generates comprehensive case studies

**Tech:** Analysis frameworks, Knowledge Brain integration

---

### 5. knowledge_brain
**Purpose:** Multi-disciplinary thinking system
- Understands human behavior across disciplines
- Connects insights from different domains
- Powers analysis for other agents

**Tech:** Multi-modal knowledge integration

---

## Project Structure

Each agent follows this standard structure:

```
agent-name/
├── .env                    # Secrets (gitignored)
├── .gitignore
├── requirements.txt
├── README.md
├── CLAUDE.md              # Development patterns
├── prompts/               # LLM prompts as .txt files
├── src/
│   └── agent_name/
│       ├── __init__.py
│       ├── schemas.py     # Pydantic models
│       ├── tools.py       # API integrations
│       └── main_loop.py   # Orchestration
├── scripts/
│   └── run_agent.py       # Entry point
├── tests/
│   └── inputs/            # Test data
└── logs/                  # Runtime logs
```

## Shared Utilities

All agents can import shared utilities from `../shared/agent_utils`:
- Token cost calculator
- LLM client wrappers
- Pydantic validation helpers
- More utilities coming soon

## Usage

```bash
# Navigate to specific agent
cd notes-agent

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure .env file
cp .env.example .env  # Edit with your API keys

# Run
python scripts/run_agent.py
```
