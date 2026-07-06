#!/bin/bash

# Script to add Todoist MCP to Claude Code settings

CLAUDE_JSON="$HOME/.claude.json"
BACKUP="$HOME/.claude.json.backup.$(date +%s)"

echo "Creating backup at: $BACKUP"
cp "$CLAUDE_JSON" "$BACKUP"

# Get the Todoist API token
echo ""
echo "Enter your Todoist API token (get it from https://todoist.com/prefs/integrations):"
read -r TODOIST_TOKEN

if [ -z "$TODOIST_TOKEN" ]; then
  echo "Error: Token cannot be empty"
  exit 1
fi

# Path to the built MCP server
MCP_PATH="/Users/snehamehrin/Desktop/ai_product_intelligence/infrastructure/mcp-todoist/build/index.js"

if [ ! -f "$MCP_PATH" ]; then
  echo "Error: MCP server not found at $MCP_PATH"
  echo "Run 'npm run build' first"
  exit 1
fi

echo ""
echo "MCP Configuration:"
echo "  Path: $MCP_PATH"
echo "  Token: ${TODOIST_TOKEN:0:10}..."
echo ""
echo "Add this to your .claude.json under the project mcpServers section:"
echo ""
cat <<EOF
"todoist": {
  "command": "node",
  "args": [
    "$MCP_PATH"
  ],
  "env": {
    "TODOIST_API_TOKEN": "$TODOIST_TOKEN"
  },
  "dangerouslySkipPermissions": true
}
EOF

echo ""
echo ""
echo "MANUAL STEPS:"
echo "1. Open $CLAUDE_JSON in your editor"
echo "2. Find the section for: \"/Users/snehamehrin/Desktop/ai_product_intelligence\""
echo "3. Locate the \"mcpServers\": {} line (around line 534)"
echo "4. Replace {} with the configuration above"
echo "5. Save and restart Claude Code"
echo ""
echo "Backup created at: $BACKUP"
