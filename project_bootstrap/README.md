# project-bootstrap

A CLI tool to scaffold AI agent and application projects with opinionated, golden templates.

Think of it as `create-react-app` but for AI agents, APIs, CLIs, and web apps.

## Installation

```bash
# From this directory
pip install -e .

# Now available globally:
bootstrap --help
```

## Quick Start

```bash
# Create a Python agent project
bootstrap my-agent --type agent --lang python

# Create a FastAPI API project
bootstrap my-api --type api

# Create a CLI tool
bootstrap my-cli --type cli

# Create a Streamlit web app
bootstrap my-webapp --type webapp
```

After creation:

```bash
cd my-agent
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m src.my_agent.main
```

## Architecture

```
project-bootstrap/
├── src/bootstrap/
│   ├── cli.py              # Entry point & arg parsing
│   ├── scaffold.py         # Directory creation
│   ├── git.py              # Git initialization
│   ├── environment.py      # Venv & dependency setup
│   ├── configs.py          # Config file generation
│   └── templates/          # Golden template files
│       ├── gitignore/
│       ├── env/
│       ├── claude_md/
│       ├── python/         # Python templates (Jinja2)
│       └── node/           # Node templates (Jinja2)
└── tests/
    ├── test_scaffold.py
    └── test_cli.py
```

## What Gets Generated

When you run `bootstrap my-project --type agent`, you get:

```
my-project/
├── .env                         # Secrets (gitignored)
├── .env.example                 # Template for .env
├── .gitignore                   # Language-specific ignore rules
├── CLAUDE.md                    # AI agent development guide
├── requirements.txt             # Python dependencies
├── README.md                    # Placeholder
│
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── config.py            # Load .env, validate settings
│       └── main.py              # Entry point with logging
│
├── tests/
│   ├── __init__.py
│   ├── inputs/                  # Test data (10-15 samples)
│   └── test_main.py             # Starter tests
│
└── logs/                        # Runtime logs (gitignored)
    └── (empty)
```

## Project Types

### `agent`
AI agent that uses Claude API. Includes:
- Anthropic SDK
- Tenacity for retries
- Loguru for observability
- Pydantic for schemas

### `api`
FastAPI REST API. Includes:
- FastAPI + Uvicorn
- Pydantic validation
- Health check endpoint

### `cli`
Command-line tool using Click. Includes:
- Click framework
- Argument/option parsing
- Command groups support

### `webapp`
Streamlit web application. Includes:
- Streamlit
- Session state management
- Component patterns

## Language Support

### Python (default)
- Virtual environment (`.venv/`)
- pip dependencies (`requirements.txt`)
- Pytest configuration
- Loguru logging

### Node.js
- npm dependencies (`package.json`)
- TypeScript support (tsconfig.json)
- ESM modules

## Customization

To customize what gets generated, edit the template files in `src/bootstrap/templates/`:

- `.env` defaults: Edit `env/default.env`
- CLAUDE.md content: Edit `claude_md/base.md` and type-specific files
- Python defaults: Edit `python/config.py.j2` and `python/main.py.j2`
- Dependencies: Edit `python/requirements-*.txt`

## Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=bootstrap tests/

# Format code
black src/bootstrap tests/

# Lint
ruff check src/bootstrap tests/
```

## Features

- ✅ Opinionated defaults (you'll use these patterns)
- ✅ Template composition by project type
- ✅ Single-command setup (venv + deps + configs)
- ✅ Git initialization with language-specific .gitignore
- ✅ Jinja2 template rendering for customization
- ✅ Works with Python 3.11+
- ✅ Tested end-to-end

## Usage in CLAUDE.md

Add to your root CLAUDE.md:

```markdown
## New Project Setup

Before starting any new project:

1. Run `bootstrap <project-name> --type agent --lang python`
2. Follow the setup instructions printed by the CLI
3. See the generated CLAUDE.md for project-specific guidelines
```

## License

MIT
