# Project: {{ project_name }}

This project was bootstrapped with `project-bootstrap` CLI.

## General Rules

- Always add dependencies to `requirements.txt` (at project root)
- Use `.env` files for secrets (gitignored, not committed)
- Always add `.env` to `.gitignore`
- Run tests with `pytest` before committing

## Python Setup

- Virtual environment: `source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Run tests: `pytest`
- Run linter: `ruff check .`
- Format code: `black .`

## Project Structure

```
{{ project_name }}/
├── .env                    # Secrets (gitignored, NEVER commit)
├── .gitignore              # Generated at bootstrap
├── requirements.txt        # All dependencies
├── .venv/                  # Virtual environment (gitignored)
├── README.md               # Project overview
│
├── src/
│   └── {{ package_name }}/
│       ├── __init__.py
│       ├── config.py       # Configuration from env vars
│       └── main.py         # Main logic
│
├── tests/
│   ├── __init__.py
│   ├── inputs/             # Test data samples
│   └── test_*.py           # Test files
│
└── logs/                   # Runtime logs (gitignored)
```

## Key Principles

- **Schemas First** — Use Pydantic models for all external data
- **Validate Everything** — Never trust raw LLM output or API responses
- **Log Observably** — Include input, decision, confidence, and result in logs
- **Test Early** — Run tests frequently during development
- **Commit Often** — Small, focused commits with clear messages

## Testing

Place test inputs in `tests/inputs/` and run with:
```bash
pytest -v
```

Test with multiple cases:
- Happy path (expected input)
- Edge case (empty, null, missing fields)
- Invalid input (wrong types, constraints)
