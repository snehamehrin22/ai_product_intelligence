# Shared Utilities

Reusable utilities and tools that are used across multiple projects.

## Contents

### 1. agent_utils
**Purpose:** Core utilities for building AI agents
- **Token cost calculator:** Calculate costs for OpenAI, Anthropic, DeepSeek
- **LLM client wrappers:** Unified interface for different providers (coming soon)
- **Pydantic validation helpers:** Auto-validate LLM outputs (coming soon)
- **Prompt management:** Load and version control prompts (coming soon)

**Installation:**
```bash
cd agent_utils
pip install -e .
```

**Usage:**
```python
from agent_utils import calculate_cost

tokens = {"prompt_tokens": 1000, "completion_tokens": 500}
cost = calculate_cost(provider="openai", model="gpt-4o", tokens=tokens)
print(f"Total: ${cost['total_cost']:.4f}")
```

---

### 2. project_bootstrap
**Purpose:** CLI tool to scaffold AI agent projects
- Generates complete project structure in seconds
- Follows CLAUDE.md best practices
- Includes templates for schemas, prompts, tests

**Installation:**
```bash
cd project_bootstrap
pip install -e .
```

**Usage:**
```bash
# Create new agent project
project-bootstrap my-agent --template ai-agent

# Generates:
# - Folder structure
# - requirements.txt
# - .env template
# - .gitignore
# - Pydantic schemas skeleton
# - Test structure
```

---

## Adding New Utilities

When creating a new shared utility:

1. Create folder in `shared/`
2. Add `README.md` explaining purpose and usage
3. Include `setup.py` for pip installation
4. Add tests
5. Update this README
6. Use in at least 2 projects before considering "battle-tested"

## Philosophy

These utilities exist because:
- **DRY principle:** Don't repeat yourself across projects
- **Battle-tested:** Each utility comes from real production use
- **Zero config:** Work out of the box with sensible defaults
- **Type safe:** Use Pydantic and type hints throughout
- **Cost aware:** Always track token usage and costs

## Roadmap

See individual utility folders for detailed roadmaps.

**Coming soon:**
- Unified LLM client (OpenAI, Anthropic, DeepSeek)
- Pydantic validation decorators
- Test data generators
- Observability dashboard
- Prompt versioning system
