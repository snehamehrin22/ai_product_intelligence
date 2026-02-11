# Infrastructure

Infrastructure projects, MCP servers, and deployment/installation guides.

## Contents

### 1. supabase_mcp_server
**Purpose:** MCP server for Claude Desktop + Supabase integration
- Provides intelligent access to Supabase database through natural language
- Works with Claude Desktop app
- Enables database queries via conversation

**Tech:** Model Context Protocol (MCP), Supabase

**Setup:**
```bash
cd supabase_mcp_server
# Follow README.md for Claude Desktop configuration
```

---

### 2. open_claw_installation
**Purpose:** VPS setup guide for AI tools
- Complete setup for OpenClaw (messaging AI)
- Claude Code (terminal AI) configuration
- Hostinger VPS deployment instructions

**Use case:** Deploy AI assistants to remote servers

---

### 3. migration-scripts
**Purpose:** Database migration and data transfer scripts
- Scripts for moving data between systems
- Schema migrations
- Data transformation utilities

**Note:** Review scripts before running - may need updates for current schema

---

## What Goes Here

Infrastructure projects include:
- **MCP servers:** Model Context Protocol integrations
- **Deployment guides:** VPS/cloud setup instructions
- **Migration tools:** Database and data transfer utilities
- **Configuration templates:** Reusable configs for infrastructure
- **Installation scripts:** Automated setup for tools/services

## Not Infrastructure

These belong elsewhere:
- **AI agents:** → `agents/` folder
- **Shared utilities:** → `shared/` folder
- **Project templates:** → `shared/project_bootstrap`

## Usage

Each infrastructure project has its own README with:
- Prerequisites
- Installation steps
- Configuration guide
- Troubleshooting

Always read the project-specific README before proceeding.
