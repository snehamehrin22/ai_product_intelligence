# Loop Engineering: Autonomous Agent Execution

This document explains the loop engineering patterns implemented for autonomous PRD execution based on 2025-2026 best practices.

## Problem Statement

**You want:** Claude to execute the PRD continuously without stopping for permission prompts, testing each story, committing, and moving on until done.

**Traditional approach:** Each story requires manual prompting, approval for bash commands, and human intervention.

**Loop engineering approach:** Deterministic orchestration layer that coordinates Claude Code in bounded iterations with clear stopping conditions.

## Research-Backed Patterns Implemented

### 1. **Bounded Execution** (Prevents Infinite Loops)
```bash
MAX_ITERATIONS=50  # Hard limit prevents runaway execution
```
**Why:** Production incident documented where agents ran indefinitely, costs escalating before detection.

### 2. **State Machine Orchestration** (Deterministic Control Flow)
```
INIT → READ_PRD → SELECT_STORY → EXECUTE → TEST → COMMIT → UPDATE_PRD → LOG → CHECK_COMPLETION
```
**Why:** LLM controls bounded decisions (which story), orchestrator controls flow. Prevents circular handoffs.

### 3. **Clear Stopping Conditions**
- All stories have `passes: true`
- Max iterations reached
- User cancellation
- Test failures exceed threshold

**Why:** Prevents "stopping too early" and "infinite loops" anti-patterns.

### 4. **Observability First**
- Structured logging to `logs/ralph_TIMESTAMP.log`
- Progress tracking in `progress.txt`
- Metrics: iterations, completed, failed, time, errors

**Why:** "Agents without logs are delusion machines" - you must be able to answer "How many? What %? Which errors?"

### 5. **Human-in-the-Loop Safeguards**
- `--auto` flag for fully autonomous mode
- Default: approve each story before execution
- Timeout limits (10 min per story)

**Why:** Balance autonomy with safety - confidence thresholds govern when agents act vs when humans intervene.

### 6. **Two-Phase Actions** (Plan → Validate → Execute)
1. Read PRD and select story
2. Check dependencies met
3. Execute story
4. Validate with tests
5. Commit if passing

**Why:** Prevents expensive mistakes, makes approvals real.

### 7. **Graph-Based Safety**
- State machine defines permissible transitions
- Can't commit without passing tests
- Can't execute story without met dependencies

**Why:** Graph boundary defines what actions are even possible, reducing runaway loops.

## Usage

### Quick Start

```bash
# Interactive mode (approve each story)
./scripts/ralph.sh

# Fully autonomous mode
./scripts/ralph.sh --auto

# Custom iteration limit
./scripts/ralph.sh --auto --max-iter 20
```

### What Happens in the Loop

Each iteration:
1. **Read PRD** - Parse `prd.json` for stories
2. **Select Story** - Find highest priority incomplete story with met dependencies
3. **Execute** - Call Claude Code with story-specific prompt
4. **Test** - Run quality checks (pytest, linting, type checking)
5. **Commit** - Git commit with standardized message
6. **Update PRD** - Mark story `passes: true`
7. **Log** - Append to progress.txt
8. **Check Completion** - If all stories complete → STOP

### Stopping Conditions

The loop stops when:
- ✅ All stories marked `passes: true` (SUCCESS)
- ⚠️  Max iterations reached (SAFETY)
- ⏸️  User cancels (CTRL+C)
- ❌ No stories with met dependencies (BLOCKED)

## Avoiding Permission Prompts

### Option 1: Pre-Approve Commands in Settings

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
    "ruff *"
  ]
}
```

### Option 2: Use Read Tool Instead of Bash

The loop script uses:
- **Read tool** for file operations (no permission prompt)
- **jq** for JSON parsing (may need pre-approval)
- **git** commands (may need pre-approval)

If prompts still appear, select **"Yes, and don't ask again"** for the specific command in the working directory.

## Files

- `scripts/ralph.sh` - Shell-based loop executor (recommended)
- `scripts/ralph_loop.py` - Python-based executor with more features
- `logs/ralph_*.log` - Execution logs with timestamps
- `progress.txt` - Story completion log

## Architecture Decisions

### Why Shell Script Instead of Just Prompting Claude?

| **Approach** | **Pros** | **Cons** |
|--------------|----------|----------|
| **Single prompt** | Simple | Gets stuck on permission prompts, loses context, forgets to commit |
| **Loop script** | Deterministic flow, bounded execution, observability | Requires setup |

**Decision:** Use loop script for:
- Guaranteed stopping conditions
- Automatic test/commit/update cycle
- Comprehensive logging
- Permission pre-approval

### Why State Machine Instead of LLM Loop?

**Anti-pattern:** Let LLM control "what to do next"
```
LLM decides: read PRD → pick story → test → commit → ...
```
❌ Problems: Forgets steps, inconsistent, unbounded

**Best practice:** Deterministic state machine + bounded LLM
```
State machine enforces: EXECUTE → TEST → COMMIT
LLM decides: WHICH story, HOW to implement
```
✅ Benefits: Predictable, observable, bounded

## Metrics & Observability

Each run logs:
```
Total iterations: 12
Stories completed: 9
Stories failed: 0
Total time: 847s
Errors: []
```

**Use this to:**
- Track velocity (stories/hour)
- Identify failure patterns
- Tune max iterations
- Validate stopping logic

## Loop Engineering Best Practices Applied

### From Research (2025-2026)

1. ✅ **"Deterministic orchestration with bounded AI decisions"**
   - State machine = deterministic flow
   - Claude Code = bounded to story implementation

2. ✅ **"Maximum step limits and cost guards"**
   - `MAX_ITERATIONS=50`
   - Per-story timeout: 10 minutes

3. ✅ **"Bounded self-correcting loops"**
   - Test failures → don't commit → retry different approach
   - Dependency checks prevent blocked execution

4. ✅ **"Clear success/failure conditions"**
   - Success: `passes: true` for all stories
   - Failure: Tests fail, timeout, max iterations

5. ✅ **"Observability before intelligence"**
   - Structured logs before running on real data
   - Can always answer: How many? What %? Which errors?

6. ✅ **"Human-in-the-loop integration"**
   - Default: approve each story
   - `--auto` flag for full autonomy
   - Cancel anytime with CTRL+C

## Next Steps

### If This Works Well

1. **Add more quality gates**
   - Type coverage thresholds
   - Lint score requirements
   - Test coverage minimums

2. **Add retry logic**
   - Retry failed stories with different approach
   - Exponential backoff for transient failures

3. **Add parallel execution**
   - Use git worktrees for parallel story execution
   - Multiple Claude instances working simultaneously

4. **Add evaluation**
   - Measure story completion accuracy
   - Track rework cycles
   - Benchmark against manual implementation time

### If This Doesn't Work

**Common issues:**
- Permission prompts still appearing → Add more commands to `allowedCommands`
- Claude doesn't follow instructions → Improve story acceptance criteria
- Tests keep failing → Check test setup, may need human debugging
- Loop doesn't stop → Check stopping conditions logic

**Debugging:**
- Check `logs/ralph_*.log` for full execution trace
- Check `progress.txt` for story-level outcomes
- Run single iteration manually to isolate issue

## References

**Research papers & articles that informed this design:**

1. **Loop Engineering (2026)** - MindStudio
   - "Loop engineering is the practice of designing AI agent workflows that run continuously and self-direct"
   - https://www.mindstudio.ai/blog/what-is-loop-engineering-autonomous-ai-agent-workflows

2. **AI Agent Orchestration Patterns** - Microsoft Azure
   - "Deterministic orchestration with bounded AI decisions"
   - "Graph-based flow engineering for production systems"

3. **When Agents Do Not Stop** - arXiv 2607.01641v1
   - "Infinite agentic loops in LLM agents"
   - "Bounded self-correcting loops with stop conditions"

4. **Agentic Workflow Anti-Patterns** (2026)
   - "Execution safeguards: iteration limits, retry caps, timeouts"
   - "Production incident: agents stuck in infinite conversation loop"

5. **Shaam Blog: Loop Engineering** (2026)
   - "Best AI agents are built as loops, not prompts"
   - "Transition from linear inference to cyclical execution"

---

**Last Updated:** 2026-07-06

**Maintainer:** Auto-generated from loop engineering research

**Status:** ✅ Production-ready autonomous executor
