## Agent-Specific Patterns

### Architecture Pattern

Keep your agent in three layers:

1. **Schemas** (`src/{{ package_name }}/schemas.py`)
   - Define all data models with Pydantic
   - This is the single source of truth

2. **Tools** (`src/{{ package_name }}/tools.py`)
   - Pure functions that take input, call APIs, return results
   - No side effects except API calls
   - All return values must match schemas

3. **Main Loop** (`src/{{ package_name }}/main.py`)
   - Orchestration only
   - Call LLM with prompt
   - Validate response with Pydantic
   - Call tools based on LLM decision
   - Repeat until done

### LLM Integration

Always validate LLM output:

```python
from pydantic import BaseModel
import json

class MyResponse(BaseModel):
    decision: str
    confidence: float

# Get LLM response
response_text = client.messages.create(...)
data = json.loads(response_text)

# Validate it
validated = MyResponse(**data)  # Throws if invalid
```

### Prompts

Store prompts as files in `prompts/`:

```
{{ project_name }}/
├── prompts/
│   ├── system.txt
│   └── user_task.txt
```

Load them in code:

```python
def load_prompt(name: str) -> str:
    with open(f"prompts/{name}.txt") as f:
        return f.read()

system = load_prompt("system")
```

### Testing Agents

Create representative test inputs in `tests/inputs/` and verify:

1. LLM response validation doesn't crash
2. Tools execute correctly with valid input
3. Full loop completes end-to-end

```bash
pytest -v tests/test_main.py
```

### Logging

Always log decisions:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Agent decision",
    extra={
        "decision": decision,
        "confidence": confidence,
        "action": "calling_tool",
    }
)
```
