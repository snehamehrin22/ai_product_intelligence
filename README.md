# AI Product Intelligence

A collection of AI agents, shared utilities, and infrastructure for product intelligence and content generation.

## Project Structure

```
ai_product_intelligence/
├── agents/                    # AI agent projects
│   ├── notes-agent           # Journal classification (Notion → Supabase)
│   ├── reddit_sentiment_analyzer  # Brand sentiment from Reddit
│   ├── ai_content_intelligence    # Content carousel generation
│   ├── app_analysis_system        # Deep app case studies
│   └── knowledge_brain            # Multi-disciplinary thinking system
│
├── shared/                    # Reusable utilities
│   ├── agent_utils           # Token calculator, LLM wrappers, validation
│   └── project_bootstrap     # CLI to scaffold new agent projects
│
├── infrastructure/            # MCP servers, deployment guides
│   ├── supabase_mcp_server   # Claude Desktop + Supabase integration
│   ├── open_claw_installation # VPS AI setup guides
│   └── migration-scripts      # Database migration tools
│
├── CLAUDE.md                  # Global development guidelines
├── prd.json                   # Project requirements
└── progress.txt               # Development progress log
```

## Quick Start

### Working with Agents

```bash
# Navigate to specific agent
cd agents/notes-agent

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env  # Add your API keys

# Run
python scripts/run_agent.py
```

### Using Shared Utilities

```bash
# Install agent_utils
cd shared/agent_utils
pip install -e .

# Use in your project
from agent_utils import calculate_cost
```

### Creating New Agents

```bash
# Use project_bootstrap CLI
cd shared/project_bootstrap
pip install -e .

# Generate new agent
project-bootstrap my-new-agent --template ai-agent
```

## Philosophy

### Agent Design Principles
1. **Schemas first** - Pydantic models as single source of truth
2. **Prompts as files** - Store in `prompts/*.txt` for version control
3. **Token awareness** - Always track and log LLM costs
4. **Type safety** - Use type hints and validation throughout
5. **Observability** - Log decisions, confidence scores, errors

### Code Organization
- **Logic** → `src/agent_name/` (pure functions, NO `main()`)
- **Execution** → `scripts/` (has `main()`, imports from src)
- **Prompts** → `prompts/` (easy to edit, version controlled)
- **Tests** → `tests/inputs/` (10-15 diverse samples)

### Project Structure
Every agent follows this template:
```
agent-name/
├── .env                    # Secrets (gitignored)
├── requirements.txt
├── prompts/               # LLM prompts as .txt files
├── src/agent_name/
│   ├── schemas.py         # Pydantic models
│   ├── tools.py           # API integrations
│   └── main_loop.py       # Orchestration
├── scripts/
│   └── run_agent.py       # Entry point
└── tests/
    └── inputs/            # Test data
```

## Development Guidelines

See `CLAUDE.md` for detailed guidelines including:
- Project setup workflow
- Pydantic validation patterns
- LLM provider selection (OpenAI vs Anthropic vs DeepSeek)
- Token tracking requirements
- Testing best practices
- Environment variable management

## Key Learnings

From retros (see `~/.claude/retros/`):
- **56-89% of time** is spent on boilerplate → Solution: `project_bootstrap`
- **52% of debugging** is credentials/permissions → Solution: `agent_utils` validators
- **Token tracking** should be mandatory, not optional
- **Pydantic validation** prevents 99.8% of data corruption issues

## Tech Stack

**LLM Providers:**
- OpenAI (GPT-4o) - Structured JSON output
- Anthropic (Claude 3.5 Sonnet) - Complex reasoning
- DeepSeek - Cost-effective alternative

**Storage:**
- Supabase (PostgreSQL)
- Notion (journal entries)
- Google Sheets (data staging)

**APIs:**
- PhantomBuster (data scraping)
- Reddit API (brand monitoring)
- Perplexity (enrichment)

## Active Projects

**Production:**
- notes-agent (journal classification)
- ai_content_intelligence (carousel generation)

**Development:**
- Client acquisition pipeline (lead scoring)
- Triage agent (cognitive categorization)

**Utilities:**
- Token cost calculator ✅
- Project bootstrap CLI ✅
- LLM client wrappers 🚧
- Pydantic validation decorators 🚧

## Contributing

When adding new projects:

1. **Determine category:**
   - Agent? → `agents/`
   - Reusable utility? → `shared/`
   - Infrastructure/deployment? → `infrastructure/`

2. **Follow structure:**
   - Use standard project layout
   - Include README.md
   - Add .env.example (never commit .env)
   - Write tests with diverse inputs

3. **Update docs:**
   - Add to category README
   - Update this root README
   - Document learnings in CLAUDE.md

## Documentation

- `/agents/README.md` - Agent catalog
- `/shared/README.md` - Shared utilities guide
- `/infrastructure/README.md` - Infrastructure projects
- `CLAUDE.md` - Development methodology
- `~/.claude/retros/` - Session retrospectives

---

**Last updated:** February 11, 2026
