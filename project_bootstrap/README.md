# project-bootstrap

A CLI tool to scaffold AI agent projects in seconds with opinionated, production-ready templates.

**Focus:** AI agents only. Web apps, APIs, and CLIs have been removed to optimize for agent development.

## Installation

```bash
# From this directory
pip install -e .

# Now available globally:
bootstrap --help
```

## Quick Start

```bash
# Create an AI agent project
bootstrap my-agent --llm openai

# With all features (default)
bootstrap my-agent --llm openai --features pydantic,token-tracking,tests

# Skip venv creation (if you're in an existing venv)
bootstrap my-agent --llm openai --no-venv

# Skip git initialization
bootstrap my-agent --llm openai --no-git
```

After creation:

```bash
cd my-agent
source .venv/bin/activate
# Add your API keys to .env
pytest -v
python scripts/run_agent.py --input "test input"
```

## What Gets Generated

When you run `bootstrap my-agent --llm openai`, you get:

```
my-agent/
├── .env                         # API keys (gitignored)
├── .env.example                 # Template
├── .gitignore                   # Python-specific ignore rules
├── requirements.txt             # Auto-generated based on features
├── pyproject.toml               # Project config + pytest settings
├── README.md                    # Project overview
│
├── src/
│   └── my_agent/
│       ├── __init__.py          # Package exports
│       ├── schemas.py           # Pydantic models (SINGLE SOURCE OF TRUTH)
│       ├── utils.py             # load_prompt(), track_tokens(), log_tokens()
│       └── main.py              # Core logic with LLM setup
│
├── prompts/                     # LLM prompts as .txt files (version controlled)
│   ├── system_prompt.txt
│   └── user_prompt.txt
│
├── scripts/
│   └── run_agent.py             # Entry point with CLI args
│
├── tests/
│   ├── __init__.py
│   ├── inputs/                  # Test data
│   │   ├── sample_01.txt
│   │   └── sample_02.txt
│   ├── outputs/                 # Results (gitignored)
│   └── test_main.py             # Starter tests
│
└── logs/                        # Runtime logs (gitignored)
    └── token_usage.jsonl        # Auto-populated by utils.py
```

## Features

### Core (Always Included)
- Python 3.11+ support
- Virtual environment setup
- `.env` file management
- Git initialization
- Basic project structure

### Optional Features (via `--features`)

#### `pydantic` (default: enabled)
- Pydantic models for validation
- Schema-first development
- Type safety for LLM I/O

#### `token-tracking` (default: enabled)
- Automatic token usage tracking
- JSONL logging to `logs/token_usage.jsonl`
- Cost calculation utilities

#### `tests` (default: enabled)
- pytest setup
- Sample test inputs
- Test coverage configuration

## LLM Provider Support

### OpenAI (--llm openai)
- Uses `openai>=1.0.0`
- Structured output with `response_format={"type": "json_object"}`
- Built-in token tracking

### DeepSeek (--llm deepseek)
- Uses OpenAI SDK with custom base_url
- Cost-effective alternative

### Anthropic (--llm anthropic)
- Uses `anthropic>=0.7.0`
- Claude API integration

## Key Patterns Included

### 1. Prompt Management
Prompts are stored as `.txt` files in `prompts/`:
```python
from utils import load_prompt

system_prompt = load_prompt("system_prompt")
```

### 2. Token Tracking
Built-in utilities for tracking LLM costs:
```python
from utils import track_tokens, log_tokens

tokens = track_tokens(response)
log_tokens(tokens, "my_operation")
```

### 3. Pydantic Validation
Never trust raw LLM output:
```python
from schemas import AgentOutput

data = json.loads(llm_response)
validated = AgentOutput(**data)  # Throws ValidationError if invalid
```

### 4. Test-Driven Development
Sample inputs in `tests/inputs/`, run with:
```bash
pytest -v
```

## Development

```bash
# Install in editable mode
cd project_bootstrap
pip install -e .

# Run tests
pytest -v

# Create a test agent
bootstrap test-agent --llm openai --no-venv --no-git
```

## Philosophy

This tool embodies lessons learned from building dozens of AI agents:

1. **Prompts as files** - Version control, easy editing, non-technical collaboration
2. **Token tracking from day 1** - You can't optimize what you don't measure
3. **Schema-first** - Pydantic models catch LLM hallucinations early
4. **Test inputs matter** - Diverse test cases prevent production surprises
5. **No surprises** - Opinionated defaults that actually work

## Comparison to Old Version

| Feature | Old project-bootstrap | New project-bootstrap |
|---------|----------------------|----------------------|
| Project types | agent, api, cli, webapp | **agent only** |
| Languages | Python, Node.js | **Python only** |
| Template system | Jinja2 templates | **Direct Python generation** |
| LLM support | None | **Built-in for 3 providers** |
| Token tracking | None | **Included by default** |
| Prompt management | None | **load_prompt() utility** |
| Setup time | ~5 minutes | **~30 seconds** |

## Future Enhancements

- [ ] `--storage` flag (notion, supabase, local)
- [ ] Pre-built schemas for common tasks (triage, summarization, extraction)
- [ ] Token cost calculation by provider
- [ ] LLM client wrappers (retry logic, error handling)
- [ ] Test data generator
- [ ] Observability dashboard

## License

MIT

---

**Generated by the team at [ai_product_intelligence](https://github.com/yourusername/ai_product_intelligence)**
