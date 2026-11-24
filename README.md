# AI Product Intelligence

AI agents, shared utilities and small apps for researching consumer products and turning observations into content.

## Structure

```
ai_product_intelligence/
├── agents/                        # AI agent projects (see agents/README.md)
│   ├── cafe-review-intelligence   # Google reviews of Toronto cafes -> retention experiments
│   ├── reddit_sentiment_analyzer  # Brand sentiment from Reddit
│   └── research_agent             # Observation -> 10-15 research angles
├── reel_framework_library/        # Corpus of top Instagram reels -> script frameworks
├── instagram_hook_analyzer/       # Instagram hook scraper/analyzer (Vercel app)
├── forno_subscription_ssr/        # Semantic Similarity Rating study for Forno Cultura
├── shared/
│   ├── agent_utils                # Token calculator, validation helpers
│   └── project_bootstrap          # CLI to scaffold new agent projects
├── infrastructure/                # See infrastructure/README.md
│   ├── open_claw_installation     # VPS setup guides for OpenClaw / Claude Code
│   └── wispr-flow-mcp             # MCP server for Wispr Flow dictation history
├── CLAUDE.md / AGENTS.md          # Agent instructions (Ralph loop)
└── prd.json / progress.txt        # Ralph PRD and progress log
```

## Working on a project

Each project is self-contained with its own `requirements.txt` and `.env` (never committed).

```bash
cd agents/<project>
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # if present, then add API keys
```

See each project's `README.md` for how to run it.

## Conventions

- **Schemas first**: Pydantic models are the source of truth; never trust raw LLM output.
- **Prompts as files**: `prompts/*.txt`, version controlled.
- **Logic vs execution**: logic in `src/<name>/` (no `main()`), entry points in `scripts/`.
- **Observability**: log inputs, decisions, confidence and errors before running on real data.
- **Tests**: 10-15 varied samples in `tests/inputs/`.

## Adding a project

- Agent -> `agents/`; reusable utility -> `shared/`; deployment or MCP server -> `infrastructure/`.
- Include a README and `.env.example`, and add it to the tree above.
