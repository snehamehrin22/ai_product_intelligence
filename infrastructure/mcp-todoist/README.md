# MCP Todoist Server

Model Context Protocol server for Todoist integration.

## Features

- **Task Management**: Get, create, update, complete, and delete tasks
- **Project Management**: View and create projects
- **Comments**: Add and retrieve task comments
- **Filtering**: Filter tasks by project or label

## Setup

1. Get your Todoist API token from https://todoist.com/prefs/integrations

2. Install dependencies:
```bash
npm install
```

3. Build the server:
```bash
npm run build
```

## Configuration

Add to your Claude Code settings (`~/.claude.json`):

```json
{
  "mcpServers": {
    "todoist": {
      "command": "node",
      "args": [
        "/Users/snehamehrin/Desktop/ai_product_intelligence/infrastructure/mcp-todoist/build/index.js"
      ],
      "env": {
        "TODOIST_API_TOKEN": "your_api_token_here"
      },
      "dangerouslySkipPermissions": true
    }
  }
}
```

## Available Tools

- `get_tasks` - Get all active tasks (filter by project_id or label)
- `create_task` - Create new task (content, description, labels, priority, due date)
- `update_task` - Update existing task
- `complete_task` - Mark task as complete
- `delete_task` - Delete task permanently
- `get_projects` - List all projects
- `create_project` - Create new project
- `add_comment` - Add comment to task
- `get_comments` - Get all comments for a task

## Usage Examples

Once configured, you can use natural language with Claude:

- "Show me all my tasks"
- "Create a task 'Review PR' with priority 4 due tomorrow"
- "Add comment to task 123456 saying 'Working on this now'"
- "Complete task 789012"
- "Create a new project called 'Q1 Goals'"
