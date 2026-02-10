# AI Agent Utilities Library

**Shared utilities for building AI agents faster and better.**

This library contains reusable utilities that solve recurring problems when building AI agents. Instead of copying code between projects, import these battle-tested utilities.

## Installation

```bash
# Add to your project's requirements.txt
# Until we publish to PyPI, use local editable install:
cd /path/to/ai_product_intelligence/agents
pip install -e .
```

## Available Utilities

### 1. Token Cost Calculator ✅
Calculate costs for different LLM providers based on token usage.

```python
from agent_utils import calculate_cost

# After an LLM call
tokens = {
    "prompt_tokens": 1000,
    "completion_tokens": 500,
    "total_tokens": 1500
}

cost = calculate_cost(
    provider="openai",
    model="gpt-4o",
    tokens=tokens
)

print(f"Total cost: ${cost['total_cost']:.4f}")
print(f"Prompt: ${cost['prompt_cost']:.4f}, Completion: ${cost['completion_cost']:.4f}")
```

**Supported Providers:**
- OpenAI (GPT-4, GPT-4o, GPT-3.5-turbo)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku)
- DeepSeek

### 2. LLM Client Wrapper 🚧 (Coming Soon)
Unified interface for all LLM providers with built-in retry logic and token tracking.

```python
from agent_utils import UnifiedLLMClient

client = UnifiedLLMClient(provider="openai", model="gpt-4o")
response = client.chat(
    system_prompt="You are a helpful assistant",
    user_prompt="What is 2+2?"
)

# Automatic token tracking and cost calculation
print(f"Tokens used: {response.tokens}")
print(f"Cost: ${response.cost}")
```

### 3. Pydantic Validation Helpers 🚧 (Coming Soon)
Decorators and utilities for validating LLM outputs with automatic retry.

```python
from agent_utils import validate_llm_output
from pydantic import BaseModel

class AgentResponse(BaseModel):
    answer: str
    confidence: float

@validate_llm_output(AgentResponse, max_retries=3)
def process(input_text: str) -> AgentResponse:
    # If LLM returns invalid JSON, auto-retries
    response = call_llm(input_text)
    return response
```

### 4. Prompt Template Manager 🚧 (Coming Soon)
Advanced prompt management with versioning and A/B testing.

```python
from agent_utils import PromptManager

pm = PromptManager("prompts/")
prompt = pm.load("system_prompt", version=2, variables={"role": "analyst"})
```

## Project Structure

```
agents/
├── src/
│   ├── agent_utils/           # Shared utilities library
│   │   ├── __init__.py
│   │   ├── token_calculator.py    # ✅ Token cost calculation
│   │   ├── llm_client.py          # 🚧 Unified LLM client
│   │   ├── validation.py          # 🚧 Pydantic helpers
│   │   └── prompts.py             # 🚧 Prompt management
│   │
│   └── triage_agent/          # Example: Triage agent using the utilities
│       ├── __init__.py
│       ├── schemas.py
│       └── triage.py
│
├── tests/
│   ├── test_token_calculator.py
│   └── inputs/                # Test data for triage agent
│
├── prd.json                   # Project roadmap
├── CLAUDE.md                  # Development guidelines
└── README.md                  # This file
```

## Usage in Your Projects

### Option 1: Local Development Install
```bash
# In your agent project
cd /path/to/your-agent
source .venv/bin/activate
pip install -e /path/to/ai_product_intelligence/agents
```

### Option 2: Add to requirements.txt
```
# requirements.txt
-e /Users/snehamehrin/Desktop/ai_product_intelligence/agents
```

### Option 3: Copy utils directly (not recommended)
Copy individual utilities if you need standalone versions, but you'll miss updates.

## Development

```bash
# Install dependencies
cd agents
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest -v

# Add a new utility
# 1. Create src/agent_utils/your_utility.py
# 2. Add tests in tests/test_your_utility.py
# 3. Export in src/agent_utils/__init__.py
# 4. Update this README
# 5. Add user story to prd.json
```

## Design Principles

1. **Zero configuration by default** - Work out of the box with sensible defaults
2. **Provider agnostic** - Support multiple LLM providers with same interface
3. **Cost aware** - Always track token usage and costs
4. **Type safe** - Use Pydantic for all I/O validation
5. **Battle tested** - Each utility comes from real production use

## Pricing Data (as of Feb 2025)

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|----------|-------|----------------------|------------------------|
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-4 | $30.00 | $60.00 |
| OpenAI | GPT-3.5-turbo | $0.50 | $1.50 |
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 |
| Anthropic | Claude 3 Opus | $15.00 | $75.00 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| DeepSeek | DeepSeek-v3 | $0.27 | $1.10 |

*Prices subject to change. Check provider websites for current pricing.*

## Roadmap

See `prd.json` for detailed user stories and priorities.

- [x] Token cost calculator
- [ ] Unified LLM client
- [ ] Pydantic validation helpers
- [ ] Prompt template manager
- [ ] Test data generator
- [ ] Observability dashboard

## Example Projects Using This Library

- **triage_agent** - Cognitive triage system that categorizes streams of thought into atomic items

## Contributing

This is an internal utility library. To add features:
1. Add user story to `prd.json`
2. Implement with tests
3. Update this README
4. Use in at least one real agent project before considering "done"

## License

MIT

---

**Part of the [ai_product_intelligence](https://github.com/yourusername/ai_product_intelligence) project**
