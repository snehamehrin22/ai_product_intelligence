## API-Specific Patterns

### Framework

This project uses FastAPI for HTTP APIs.

```bash
pip install fastapi uvicorn pydantic
```

### Project Structure

```
src/{{ package_name }}/
├── __init__.py
├── config.py           # Load .env, validate config
├── schemas.py          # Pydantic models for requests/responses
├── main.py             # FastAPI app setup
└── routes/
    ├── __init__.py
    ├── health.py       # GET /health
    └── {{ api_name }}.py   # Your routes
```

### Running the Server

```bash
uvicorn src.{{ package_name }}.main:app --reload --port 8000
```

### API Response Pattern

Always return consistent response:

```python
from pydantic import BaseModel

class APIResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None

@app.post("/endpoint")
async def endpoint(request: YourRequest) -> APIResponse:
    try:
        result = await process(request)
        return APIResponse(success=True, data=result)
    except Exception as e:
        return APIResponse(success=False, error=str(e))
```

### Testing

Use pytest with FastAPI TestClient:

```python
from fastapi.testclient import TestClient
from src.{{ package_name }}.main import app

client = TestClient(app)

def test_endpoint():
    response = client.post("/endpoint", json={"key": "value"})
    assert response.status_code == 200
    assert response.json()["success"] is True
```
