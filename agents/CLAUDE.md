# AI Agent Utilities Library - Development Guide

**Purpose:** This project houses shared utilities for building AI agents. Each utility solves a recurring problem and is battle-tested in production agents.

## Project Type: Shared Python Library

This is NOT a single agent - it's a **library of reusable utilities** that multiple agent projects import.

---

# Triage Agent Patterns (Example Agent)

## LLM Setup

### DeepSeek Configuration
- Use DeepSeek with custom base_url
- Always include token tracking in API calls
- Response format: `{"type": "json_object"}` for structured output
- Default temperature: 0.2 for consistency
- Min max_tokens: 4000 (avoid truncation)

### Environment Variables Required
```bash
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...  # For structured JSON output
```

### Example Client Setup
```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# For guaranteed valid JSON
resp = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[...],
    temperature=0.2,
    max_tokens=4000
)
```

## File Structure

### Directory Layout
```
project/
├── .env                    # Secrets (gitignored)
├── .gitignore              # Must include: .env, .venv/, __pycache__/
├── requirements.txt        # All dependencies
├── .venv/                  # Virtual environment
│
├── prompts/                # LLM prompts as .txt files
│   ├── system_prompt.txt
│   └── user_prompt_template.txt
│
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── schemas.py      # Pydantic models (SINGLE SOURCE OF TRUTH)
│       ├── tools.py        # Actions only (API calls, DB writes)
│       ├── utils.py        # Helper functions (load_prompt, etc.)
│       └── main.py         # Main logic
│
├── scripts/                # Executable scripts
│   └── run_agent.py        # Entry point with main()
│
├── tests/
│   ├── inputs/             # Test data (10-15 samples)
│   │   ├── sample_01.txt
│   │   └── sample_02.txt
│   └── outputs/            # Results (gitignored)
│
└── logs/                   # Runtime logs (gitignored)
```

### Critical Rules
- **Prompts** → `prompts/` as `.txt` files (easy to edit, version-controlled)
- **Schemas** → `src/project_name/schemas.py` (Pydantic models define structure)
- **Logic** → `src/project_name/*.py` (pure functions, NO `main()`)
- **Execution** → `scripts/*.py` (has `main()`, imports from src)

## Pydantic Schema Validation (CRITICAL)

**Never trust raw LLM output. Always validate with Pydantic.**

### Define Schemas First
```python
# schemas.py
from pydantic import BaseModel, Field
from typing import List

class CognitiveBlock(BaseModel):
    """A single cognitive block."""
    block_id: str = Field(..., description="Unique ID like 'b1'")
    block_name: str = Field(..., min_length=2, max_length=50)
    block_text: str = Field(..., min_length=1)

class BlockSplitResponse(BaseModel):
    """LLM response wrapper."""
    blocks: List[CognitiveBlock] = Field(..., min_items=1)
```

### Always Validate LLM Output
```python
import json
from .schemas import BlockSplitResponse

# Get LLM response
llm_response_text = client.chat.completions.create(...)
data = json.loads(llm_response_text)

# Validate with Pydantic (throws ValidationError if invalid)
validated = BlockSplitResponse(**data)

# Now type-safe and guaranteed valid
return validated.blocks
```

**Benefits:**
- ✅ Automatic type/length/required field validation
- ✅ Catches LLM hallucinations and malformed output
- ✅ IDE autocomplete and type hints
- ✅ Self-documenting code

## Prompt Management

### Store Prompts as Files (Not Hardcoded)
```python
# src/project_name/utils.py
from pathlib import Path

def load_prompt(prompt_name: str) -> str:
    """Load prompt from prompts/ folder."""
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.txt"
    return prompt_path.read_text(encoding="utf-8")

# Usage
system_prompt = load_prompt("block_splitter_system")
```

**Benefits:**
- ✅ Version control prompt iterations
- ✅ Easy to edit without touching code
- ✅ Non-technical users can update prompts
- ✅ A/B test different prompts easily

## Token Tracking (MANDATORY)

### Always Track Token Usage
```python
def call_llm_with_tracking(prompt: str) -> tuple[str, dict]:
    """Call LLM and return response + token usage."""
    resp = client.chat.completions.create(...)

    tokens = {
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "total_tokens": resp.usage.total_tokens,
        "cost": calculate_cost(resp.usage)  # Optional
    }

    return resp.choices[0].message.content, tokens
```

### Log Token Usage
```python
import logging
from datetime import datetime

def log_token_usage(tokens: dict, operation: str):
    """Log token usage to file."""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} | {operation} | {tokens}"

    with open("logs/token_usage.log", "a") as f:
        f.write(log_entry + "\n")
```

## Testing Requirements

### Always Create Diverse Test Inputs
Create `tests/inputs/` with 10-15 samples covering:
- Basic/happy path
- Empty/edge case (no matches, empty file)
- Nested/complex structures
- Mixed content (target among noise)
- Edge cases (unusual but valid)

### Test Continuously
Run tests after every major change:
```bash
python scripts/run_agent.py --test-mode
```

### Save Outputs with Timestamps
```python
from datetime import datetime

def save_output(result, test_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"tests/outputs/{test_name}_{timestamp}.json"
    # Save result...
```

## Common Patterns

### Pattern: Load → Process → Validate → Store
```python
# 1. Load
input_data = load_input_file("tests/inputs/sample_01.txt")
system_prompt = load_prompt("system_prompt")

# 2. Process
response = call_llm(system_prompt, input_data)

# 3. Validate
validated = ResponseSchema(**json.loads(response))

# 4. Store
save_output(validated, "sample_01")
```

### Pattern: Retry on Validation Failure
```python
from pydantic import ValidationError

def process_with_retry(input_data: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = call_llm(input_data)
            validated = ResponseSchema(**json.loads(response))
            return validated
        except ValidationError as e:
            if attempt == max_retries - 1:
                raise
            # Log error and retry
            logging.warning(f"Validation failed (attempt {attempt+1}): {e}")
```

## Gotchas & Lessons Learned

### LLM Provider Quirks
- **Claude**: Wraps JSON in explanatory text → Use OpenAI for structured output
- **DeepSeek**: Good value but needs higher max_tokens to avoid truncation
- **OpenAI**: `response_format={"type": "json_object"}` guarantees valid JSON

### File Organization
- Always use absolute paths from project root
- Never hardcode paths relative to script location
- Use `Path(__file__).parent.parent` to navigate up from src/

### Environment Variables
- Load with `python-dotenv` at script entry point
- Never commit `.env` to git
- Include `.env.example` template for teammates

### Pydantic Validation
- Define schemas BEFORE writing LLM calls
- Use `Field(..., description="...")` for LLM guidance
- Test validation with invalid data first

### Token Costs
- Track tokens from day 1 (not later)
- Log every LLM call with timestamp
- Calculate costs based on provider pricing
- Monitor prompt bloat (trim unnecessary context)

## Before Starting Any Build

### Pre-flight Checklist
1. ✅ **Check Python version compatibility**
   - What's the minimum Python version?
   - Use `typing` module (not modern syntax) for backwards compatibility
   - `Union[Path, str]` not `Path | str`
   - `List[str]` not `list[str]`
   - `Optional[str]` not `str | None`

2. ✅ **Verify testing setup**
   - Set `PYTHONPATH=src` for pytest
   - Or add to `pyproject.toml`: `pythonpath = ["src"]`
   - Use `.venv/bin/python` explicitly (not system python)

3. ✅ **Check for existing tools**
   - Does `project-bootstrap` exist? Use it!
   - Are there utilities in `agents/agent_utils/`? Import them!
   - Don't rebuild what exists

4. ✅ **Read schemas/config files FIRST**
   - Don't assume structure from examples
   - Error messages often show the full schema
   - Validate before editing

5. ✅ **Ask user preferences**
   - LLM provider (OpenAI/DeepSeek/Anthropic)
   - Storage location (Notion/Supabase/Local)
   - Any special requirements

## Default Assumptions

- **Token tracking**: ALWAYS include (not optional)
- **Cost calculation**: Print after every LLM call with 💰 emoji
- **Output storage**: `tests/outputs/` (gitignored)
- **Test inputs**: Create diverse samples first (10-15 covering edge cases)
- **Prompts**: Store as `.txt` files in `prompts/`
- **Virtual env**: Always create with Python 3.8+ compatible syntax
- **Dependencies**: Add to `requirements.txt` at project root
- **.env file**: Include ALL provider keys (OpenAI, Anthropic, DeepSeek) with helpful comments

## Development Patterns

### Pattern: Documentation-First
Before writing code:
1. Create/update README.md (user perspective)
2. Create/update prd.json (requirements)
3. Write CLAUDE.md section (developer patterns)
4. Then code

**Why:** Clarifies requirements, prevents rework, serves as spec during implementation

### Pattern: Dual-Purpose Utilities
For shared utilities:
1. Build standalone package in `agents/agent_utils/` with full tests
2. Also generate inline in project templates (bootstrap)
3. Keep template in sync with package

**Why:** Advanced users can import, beginners get self-contained projects, both stay in sync

### Pattern: Batteries-Included Defaults
Don't ask users to configure:
- Token tracking: Always on
- Pydantic validation: Always included
- Tests: Always have test structure
- All LLM provider keys in .env: Always present

**Why:** Reduces decision fatigue, ensures best practices, higher adoption

### Pattern: Visibility Drives Optimization
Make important metrics impossible to miss:
```python
# Always print cost after LLM calls
print(f"💰 Cost: ${cost['total_cost']:.4f} ({tokens['total_tokens']} tokens)")
```

**Why:** Developers optimize what they measure. Cost should be as visible as latency.

## Common Mistakes & How to Avoid

### Mistake 1: Not Checking Python Version Compatibility
❌ Using `dict | None`, `list[str]` (Python 3.10+)
✅ Using `Optional[Dict]`, `List[str]` (Python 3.8+)

**Prevention:** Import from typing module from the start

### Mistake 2: Wrong pytest Setup
❌ `pip install -e .` and assuming pytest works
✅ Set `PYTHONPATH=src` or add to `pyproject.toml`

**Prevention:** Configure pytest correctly in project setup

### Mistake 3: Assuming Config Schema
❌ Editing settings.json based on examples
✅ Reading error messages that show full schema

**Prevention:** Validate against actual schema first

### Mistake 4: Manual Repetitive Edits
❌ Changing function signatures in 5 files manually
✅ Using find-and-replace or refactoring tools

**Prevention:** Ask "could this be automated?" before manual work

### Mistake 5: Not Testing Incrementally
❌ Writing all code, then running tests
✅ Testing after each file/function

**Prevention:** Run tests continuously during development

## Time-Saving Shortcuts

### Use project-bootstrap
```bash
# Don't do this:
mkdir -p src/my_agent prompts scripts tests/inputs logs
# ... 30+ more commands

# Do this:
cd ../project_bootstrap
python -m src.bootstrap.cli my-agent --llm openai
# Everything generated in 2 seconds
```

**Saves:** 40 minutes per project

### Use TypedDict for Static Data
```python
# For pricing, configs, etc. (no runtime validation needed)
from typing import TypedDict

class CostBreakdown(TypedDict):
    prompt_cost: float
    completion_cost: float
    total_cost: float
```

**Why:** Lighter than Pydantic, still get type safety

### Use JSONL for Append-Only Logs
```python
# logs/token_usage.jsonl
with open(log_file, "a") as f:
    f.write(json.dumps(log_entry) + "\n")
```

**Why:** Easy to parse, no loading entire file, append-only is safe

### Embed Small Utilities, Import Large Ones
- < 500 lines: Embed in project template (token calculator)
- > 500 lines: External package (LLM framework)

**Why:** Balance between self-contained and maintainable

## Token Cost Calculator

### Always Include
Every agent project should have:
```python
def calculate_cost(provider: str, model: str, tokens: dict) -> dict:
    """Calculate cost based on provider pricing."""
    pricing = PRICING[provider][model]
    prompt_cost = (tokens["prompt_tokens"] / 1_000_000) * pricing["input"]
    completion_cost = (tokens["completion_tokens"] / 1_000_000) * pricing["output"]
    return {
        "prompt_cost": prompt_cost,
        "completion_cost": completion_cost,
        "total_cost": prompt_cost + completion_cost,
    }
```

### Keep Pricing Updated
```python
# Last updated: February 2025
PRICING = {
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    },
    "deepseek": {
        "deepseek-chat": {"input": 0.27, "output": 1.10},
    },
}
```

**Note:** Check provider websites monthly for price changes

## Testing Best Practices

### Test Coverage for Utilities
For any shared utility:
- ✅ Happy path (normal usage)
- ✅ Each variant (all providers/models)
- ✅ Edge cases (0, large numbers, boundaries)
- ✅ Error cases (invalid input)
- ✅ Data completeness (all models have pricing)

Example: Token calculator had 14 tests covering all these

### Fix Import Issues Early
If tests fail with `ModuleNotFoundError`:
```bash
# Quick fix:
PYTHONPATH=src .venv/bin/python -m pytest tests/ -v

# Permanent fix in pyproject.toml:
[tool.pytest.ini_options]
pythonpath = ["src"]
```

## Refactoring Guidelines

### When Removing Types/Classes
1. Remove the definition
2. **Immediately grep for all usages:**
   ```bash
   rg "ProjectType" --type py
   ```
3. Update all imports and function signatures
4. Test after each file

**Why:** Prevents "cannot import X" errors later

### When Changing Function Signatures
Use find-and-replace for mechanical changes:
```bash
# Instead of manually editing 5 files:
rg -l "project_type: ProjectType" | xargs sed -i 's/project_type: ProjectType/features: List[str]/g'
```

**Saves:** 10-15 minutes on large refactors

## Lessons Learned (Feb 2026)

### ✅ What Worked
1. **Documentation-first approach** - Prevented all rework
2. **Comprehensive testing** - 14 tests caught bugs before production
3. **Dual-purpose utilities** - Library + template generation
4. **Batteries-included defaults** - Zero setup, everything works
5. **Cost visibility** - 💰 emoji makes costs impossible to ignore

### ❌ What Didn't Work
1. Assuming config schema - Always read schema first
2. Using modern Python syntax - Use typing module for compatibility
3. Not setting up pytest correctly - Add pythonpath to pyproject.toml

### 📊 ROI Data
- **Time to build productivity system:** 4 hours
- **Time saved per new agent:** 40 minutes
- **Break-even point:** 6 agent projects
- **Cumulative savings after 20 agents:** 13 hours

### 🎯 Key Insight
**Automate the common path. Make the right thing the default thing.**

Users don't want choices—they want the right answer to just work.
