# Wispr Flow MCP Server

MCP server that exposes your local Wispr Flow dictation history to Claude.

## Features

- **Search dictations** by text content, app, or date range
- **Get recent dictations** with formatted text
- **Retrieve specific dictation** by ID with full metadata
- **Usage statistics** (word count, frequency, top apps)

## Installation

1. Create virtual environment:
```bash
cd /Users/snehamehrin/Desktop/ai_product_intelligence/infrastructure/wispr-flow-mcp
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make server executable:
```bash
chmod +x server.py
```

## Configuration

Add to your Claude Code settings (`~/.claude.json`):

```json
{
  "mcpServers": {
    "wispr-flow": {
      "command": "/Users/snehamehrin/Desktop/ai_product_intelligence/infrastructure/wispr-flow-mcp/.venv/bin/python",
      "args": ["/Users/snehamehrin/Desktop/ai_product_intelligence/infrastructure/wispr-flow-mcp/server.py"]
    }
  }
}
```

## Usage

Once configured, Claude can access these tools:

### `search_dictations`
Search your dictation history:
```
Search my Wispr dictations for "mechanism"
```

### `get_recent_dictations`
Get recent dictations:
```
Show my last 5 dictations
```

### `get_dictation_by_id`
Retrieve full details:
```
Get the full text for dictation ID de232a32-ff5b-45e1-9940-500b9b831fcd
```

### `get_dictation_stats`
Get usage analytics:
```
Show my Wispr Flow stats for the last 30 days
```

## Database Location

Reads from: `~/Library/Application Support/Wispr Flow/flow.sqlite`

**Read-only access** — this MCP never modifies your Wispr Flow data.

## Privacy

- All processing happens locally
- No data leaves your machine
- Database access is read-only
- Archived dictations are excluded from searches

## Testing

Test the MCP server manually:
```bash
source .venv/bin/activate
python server.py
```

The server communicates via stdio (standard input/output) and expects MCP protocol messages.
