# Ralph Agent - Autonomous Loop Executor

Autonomous agent loop executor for PRD-driven development using Claude Code.

## Quick Start

```bash
# Navigate to learning directory
cd /Users/snehamehrin/Desktop/ai_product_intelligence/learning

# Run in interactive mode (approve each story)
./scripts/ralph.sh

# Run in fully autonomous mode
./scripts/ralph.sh --auto

# Custom max iterations
./scripts/ralph.sh --auto --max-iter 20
```

## What It Does

Ralph autonomously:
1. ✅ Reads your PRD (`prd.json`)
2. ✅ Selects highest priority incomplete story
3. ✅ Invokes Claude Code to implement it
4. ✅ Runs quality checks (tests, linting, formatting)
5. ✅ Commits changes with standardized message
6. ✅ Updates PRD to mark story complete
7. ✅ Logs progress
8. ✅ Repeats until all stories complete or max iterations reached

## Files

- `ralph.sh` - Shell-based executor (recommended, simpler)
- `ralph_loop.py` - Python-based executor (more features, more complex)
- `../logs/` - Execution logs
- `../progress.txt` - Story completion log

## Options

```
--auto           Auto-approve all actions (no prompts)
--max-iter N     Maximum loop iterations (default: 50)
--prd PATH       Path to prd.json (default: ai-todo-app/prd.json)
-h, --help       Show help message
```

## Avoiding Permission Prompts

The screenshot you showed is Claude asking permission to run `cat prd.json | jq`.

### Fix Option 1: Pre-Approve Commands

Add to `~/.claude/settings.json`:

```json
{
  "allowedCommands": [
    "cat *",
    "jq *",
    "ls *",
    "git status",
    "git add .",
    "git commit -m *",
    "pytest",
    "black *",
    "ruff *",
    "npm *"
  ]
}
```

Then restart Claude Code.

### Fix Option 2: Use the Loop Script

The loop script (`ralph.sh`) uses:
- `jq` to parse JSON (shell script reads PRD, not Claude)
- Calls Claude Code only for implementation
- No permission prompts for reading files

### Fix Option 3: Select "Don't Ask Again"

When the prompt appears, choose:
**Option 2: "Yes, and don't ask again for cat prd.json commands in /path/to/dir"**

## How It Prevents Infinite Loops

**Stopping conditions:**
- ✅ All stories marked `passes: true`
- ⚠️  Max iterations reached (default: 50)
- ⏸️  User cancels (CTRL+C)
- 🚫 No stories with met dependencies

**Bounded execution:**
- Hard iteration limit
- Per-story timeout (10 min)
- Explicit state machine (can't skip steps)

## Logs & Observability

Each run creates:
```
logs/ralph_20260706_134500.log    # Full execution trace
progress.txt                       # Story-level outcomes
```

View logs:
```bash
# Latest log
tail -f logs/ralph_*.log | tail -1

# All logs
ls -lt logs/
```

## Example Output

```
================================================================================
🚀 Ralph Agent Loop - PRD Autonomous Executor
================================================================================

[INFO] PRD: /path/to/prd.json
[INFO] Max iterations: 50
[INFO] Auto-approve: false

================================================================================
🔄 Iteration 1/50
================================================================================

[INFO] Story: US-1.1 - Backend Configuration and Databricks Connection
[INFO] Priority: P0

Acceptance Criteria:
  - FastAPI app initializes with proper project structure
  - Pydantic Settings loads environment variables from .env file
  - Databricks SQL Connector successfully connects to SQL Warehouse
  ...

Continue? [Y/n]: y

[INFO] 🤖 Invoking Claude Code to implement US-1.1...
[INFO] This may take several minutes...

[SUCCESS] Story execution completed
[INFO] Running quality checks...
[SUCCESS] Quality checks passed
[SUCCESS] Committed: feat: US-1.1 - Backend Configuration and Databricks Connection
[SUCCESS] Story US-1.1 marked complete ✅
[INFO] Progress: 1/9 stories complete

================================================================================
🔄 Iteration 2/50
================================================================================
...
```

## Troubleshooting

### "jq is not installed"
```bash
brew install jq
```

### "PRD not found"
Check path:
```bash
ls -la ai-todo-app/prd.json
```

### Tests keep failing
Run manually to debug:
```bash
cd ai-todo-app/backend
source .venv/bin/activate
pytest -v
```

### Loop stops early
Check logs:
```bash
tail -100 logs/ralph_*.log | tail -1
```

### Permission prompts still appearing
1. Add commands to `~/.claude/settings.json` (see above)
2. Or select "Yes, and don't ask again" when prompted
3. Or use `--auto` mode (proceeds without prompting)

## Architecture

See `../LOOP_ENGINEERING.md` for detailed explanation of:
- State machine design
- Stopping conditions
- Observability patterns
- Research-backed best practices (2025-2026)

## Development

To modify the loop script:

```bash
# Edit shell script
vim scripts/ralph.sh

# Test changes
./scripts/ralph.sh --max-iter 1

# Check logs
tail logs/ralph_*.log | tail -1
```

## Based On

Research from 2025-2026 on loop engineering:
- MindStudio: "Loop Engineering for Autonomous AI Workflows"
- Microsoft Azure: "AI Agent Orchestration Patterns"
- arXiv: "When Agents Do Not Stop: Infinite Agentic Loops"
- Shaam Blog: "Best AI Agents Are Built as Loops, Not Prompts"

Key principles:
- ✅ Bounded execution prevents infinite loops
- ✅ State machines enforce deterministic flow
- ✅ Observability enables debugging
- ✅ Human-in-the-loop safeguards prevent disasters

---

**Last Updated:** 2026-07-06
