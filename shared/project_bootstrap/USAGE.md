# Project Bootstrap — Usage Guide

Your `project-bootstrap` CLI is now installed and ready to use.

## Quick Start

```bash
# Create a new AI agent project
bootstrap my-agent --type agent --lang python

# Create a FastAPI REST API
bootstrap my-api --type api

# Create a Click CLI tool
bootstrap my-cli --type cli

# Create a Streamlit web app
bootstrap my-webapp --type webapp
```

All commands create a ready-to-run project with:
- ✅ Directory structure
- ✅ `.env` and `.env.example`
- ✅ `CLAUDE.md` with project-specific guidelines
- ✅ `.gitignore` (language-specific)
- ✅ `requirements.txt` (dependencies by type)
- ✅ Starter Python code (`config.py`, `main.py`, `test_main.py`)
- ✅ Git initialized

## What Each Project Type Includes

### `agent` (default)
- Anthropic SDK for Claude API
- Tenacity for retries
- Loguru for structured logging
- Pydantic for schema validation
- Best for: AI agents, autonomous systems

### `api`
- FastAPI + Uvicorn
- Pydantic request/response validation
- Health check endpoint
- Best for: REST APIs, microservices

### `cli`
- Click framework
- Argument and option parsing
- Command groups support
- Best for: Command-line tools, scripts

### `webapp`
- Streamlit
- Session state management
- Component patterns
- Best for: Data apps, dashboards, prototypes

## After Creation

```bash
cd my-agent
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m src.my_agent.main
```

## Project Structure

Every bootstrapped project gets:

```
project-name/
├── .env                    # Secrets (gitignored)
├── .env.example            # Template
├── .gitignore
├── CLAUDE.md               # Development guide (PROJECT-SPECIFIC)
├── requirements.txt
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── config.py       # Load .env, settings
│       └── main.py         # Starter code
├── tests/
│   ├── __init__.py
│   ├── inputs/             # Test data
│   └── test_main.py
├── prompts/                # For agent projects
├── logs/                   # Runtime logs
└── data/                   # Local data cache
```

## CLAUDE.md

Each project includes a `CLAUDE.md` file with:

1. **Base section** — Universal setup and conventions
2. **Type-specific section** — Project-type patterns and best practices

Examples:
- Agent projects get architecture patterns, LLM integration guidance, logging patterns
- API projects get FastAPI patterns, response schemas, testing strategies
- CLI projects get Click patterns, command structures, testing with CliRunner

## Customization

To customize what future projects get:

1. **Edit templates** in `src/bootstrap/templates/`
   - `.env` defaults: Edit `env/default.env`
   - CLAUDE.md content: Edit `claude_md/*.md`
   - Python code: Edit `python/*.j2` (Jinja2 templates)
   - Dependencies: Edit `python/requirements-*.txt`

2. **Add new project types** by extending:
   - `claude_md/yourtype.md` (guidelines)
   - `python/requirements-yourtype.txt` (dependencies)

## Integration with Your Workflow

Add to your root `CLAUDE.md`:

```markdown
## Starting a New Project

Always use bootstrap:

bash
bootstrap <name> --type agent --lang python
```

Then bootstrap will:
- Create the directory structure
- Initialize git
- Set up venv and install dependencies
- Generate all config files
- Print success message with next steps

## Flags

- `--type` — Project type: `agent`, `api`, `cli`, `webapp` (default: `agent`)
- `--lang` — Language: `python`, `node` (default: `python`)
- `--no-git` — Skip git initialization
- `--no-venv` — Skip virtual environment setup

## Examples

```bash
# Python agent (full setup)
bootstrap invoice-processor

# Node.js API (skip venv, we'll use npm)
bootstrap user-service --type api --lang node --no-venv

# Python CLI without git
bootstrap file-tool --type cli --no-git
```

## Notes

- Project names become directory names: `my-project` → `./my-project/`
- Package names convert hyphens to underscores: `my-project` → `my_project`
- All projects use Python 3.11+ (Node projects can use any Node version)
- `.env` is gitignored by default — never commit secrets
- The `.env.example` file should be checked in as a template

---

**Questions?** Check the README.md in the bootstrap repo or look at a generated CLAUDE.md for project-specific patterns.
