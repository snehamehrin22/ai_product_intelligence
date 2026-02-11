# Notes Agent - Automatic Journal Classification System

## Project Overview

**Problem:** Stream-of-consciousness journal entries in Notion are unstructured and impossible to query for patterns.

**Solution:** An autonomous AI agent that automatically processes Notion journal entries, splits them into cognitive blocks, and classifies psychological patterns.

**Goal:** Transform raw journal text into structured data that reveals:
- Trigger → Emotion → Response cycles
- Desire vs fear-based avoidance patterns
- Self-concept gaps (aspiration vs reality)
- Nervous system states and behavioral responses
- Recurring themes and patterns

---

## System Architecture (Final)

### The Pipeline

```
Notion Journal Entry
        ↓
Fetch (check processed_entries in Supabase)
        ↓
Split into Cognitive Blocks (LLM)
        ↓
Classify Each Block (LLM)
  - Core emotion
  - Themes (3-8 keywords)
  - Behavioral response
  - Nervous system state
  - Action signals
  - Optional: fear_underneath, self_concept_gap
        ↓
Enforce Confidence Threshold (≥ 0.7)
        ↓
Save to Supabase (journal_blocks table)
        ↓
Mark as Processed
        ↓
Log All Decisions (JSONL)
```

### File Structure

```
notes-agent/
├── src/notes_agent/           # Main pipeline
│   ├── main_loop.py            # Orchestration (Python controls loop)
│   ├── splitter.py             # LLM splits text into blocks
│   ├── classifiers/
│   │   └── llm_classifier.py   # LLM classifies blocks
│   ├── enforcement.py          # Confidence thresholds
│   ├── tools.py                # Notion + Supabase I/O
│   ├── logging_utils.py        # Decision logging
│   └── schemas.py              # Pydantic models (source of truth)
│
├── prompts/                    # LLM prompts (editable, version controlled)
│   ├── block_splitter_system.txt
│   └── block_classifier_system.txt
│
├── scripts/
│   └── run_pipeline.py         # Entry point
│
├── data/supabase/
│   └── schema.sql              # Database schema
│
└── logs/
    └── decisions_YYYYMMDD.jsonl
```

---

## Core Principles

### 1. LLM = Reasoning Module, NOT the OS

**Agent 1 Pattern (What We Built):**
```python
# Python controls the loop
for entry in notion_entries:
    blocks = llm.split(entry)          # LLM does ONE task
    for block in blocks:
        classification = llm.classify(block)  # LLM does ONE task
        if confidence >= 0.7:           # Python decides
            save(classification)        # Python executes
```

**Key Insight:** Python makes all control flow decisions. LLM only does reasoning tasks (split text, classify patterns).

### 2. Never Trust Raw LLM Output

**Always use Pydantic for validation:**
```python
# ❌ Bad
classification = json.loads(llm_response)  # What if LLM returns invalid data?

# ✅ Good
classification = BlockClassification(**json.loads(llm_response))  # Pydantic validates
```

**Why:** LLMs are probabilistic. They occasionally return:
- Missing required fields
- Wrong data types
- Values outside expected ranges

Pydantic catches these before they corrupt your database.

### 3. Observability Before Intelligence

**Every decision must be logged:**
```python
log_decision(
    block_id=block.block_id,
    block_text=block.block_text,
    classification=classification,
    saved=True/False,
    reason="passed_all_checks" or "confidence_too_low",
    error=None or error_message
)
```

**Why:** You need to know:
- How many blocks were processed?
- What percentage passed the confidence threshold?
- Which errors occurred most frequently?
- Are classifications improving over time?

Without logs, the agent is a black box.

### 4. Think in Invariants

**Invariants = Things that must ALWAYS be true:**
1. Every journal entry processed exactly once
2. Every classification decision logged
3. No database write without Pydantic validation
4. Confidence threshold ≥ 0.7 enforced before saving
5. LLM never controls system logic (Python does)

**How we enforce:**
- `processed_entries` table in Supabase (idempotency)
- Pydantic validation before all writes
- `should_save()` function checks confidence
- Deterministic control flow in `main_loop.py`

### 5. Clean Separation of Concerns

**Modules have ONE job:**
- `schemas.py` - Data structures (Pydantic models)
- `splitter.py` - LLM splitting logic ONLY
- `classifiers/llm_classifier.py` - LLM classification ONLY
- `enforcement.py` - Business rules ONLY
- `tools.py` - External I/O ONLY (Notion, Supabase)
- `logging_utils.py` - Observability ONLY
- `main_loop.py` - Orchestration ONLY

**No mixing:** LLM code doesn't touch database. Database code doesn't do validation. Validation doesn't do logging.

---

## System Invariants

**What must ALWAYS be true:**
1. Every journal block processed exactly once
2. Every classification decision logged (input, decision, confidence, timestamp)
3. No database write without Pydantic validation passing
4. LLM never controls retry logic or modifies memory directly
5. Confidence threshold ≥ 0.7 enforced before saving classification

---

## Classification Schema

### Fields Extracted by LLM

**Required:**
- `block_id`: str - Unique identifier (e.g., "b1", "b2")
- `block_text`: str - The actual text content
- `themes`: List[str] - 3-8 keyword themes
- `core_emotion`: str - Primary emotion detected
- `nervous_system_state`: str - Physiological state
- `behavioral_response`: str - Action pattern
- `action_signal`: str - Directional impulse
- `confidence`: float - LLM certainty (0.0-1.0)

**Optional:**
- `fear_underneath`: str - Unstated fears or blockers
- `self_concept_gap`: str - Aspiration vs reality mismatch
- `action_note`: str - Concrete action suggestion

---

## Git Worktrees for Parallel Testing

### Setup

We use **git worktrees** to test multiple prompt variants in parallel without switching branches:

```bash
# List all worktrees
git worktree list

# Current setup:
# - triage-agent-prompt1 → test/prompt1 branch
# - triage-agent-prompt2 → test/prompt2 branch
```

### Worktree Structure

```
ai_product_intelligence/agents/
├── triage-agent/              # Main worktree (master branch)
├── triage-agent-prompt1/      # Prompt1 testing (test/prompt1 branch)
└── triage-agent-prompt2/      # Prompt2 testing (test/prompt2 branch)
```

### Usage Pattern

**1. Edit prompts in each worktree:**
```bash
# Terminal 1: Prompt1 testing
cd triage-agent-prompt1/agents/triage-agent
# Edit prompts/layer1_triage_system.txt
python scripts/test_layer1.py

# Terminal 2: Prompt2 testing
cd triage-agent-prompt2/agents/triage-agent
# Edit prompts/layer1_triage_system.txt
python scripts/test_layer1.py
```

**2. Output results to separate Google Sheets:**
```bash
# In prompt1 worktree - writes to GOOGLE_SHEET_PROMPT1_ID
python test_sheets_quick.py

# In prompt2 worktree - writes to GOOGLE_SHEET_PROMPT2_ID
python test_sheets_quick.py
```

**3. Compare results:**
- Open both sheets side-by-side
- Evaluate which prompt produces better classifications
- Keep the winner, merge back to master

**4. Clean up when done:**
```bash
# Keep the winning prompt in master
git worktree remove triage-agent-prompt1
git worktree remove triage-agent-prompt2
git branch -d test/prompt1 test/prompt2
```

### Benefits

- ✅ Test multiple prompts simultaneously
- ✅ No branch switching (avoids .env/venv disruption)
- ✅ Each worktree has its own working directory
- ✅ Results go to separate Google Sheets for easy comparison
- ✅ Faster iteration (run both tests in parallel)

---

## Google Sheets Integration

### Setup

**1. Credentials:**
- Service account JSON at: `config/google_service_account.json`
- Added to `.gitignore` (NEVER commit)

**2. Configuration in `.env`:**
```bash
GOOGLE_SHEET_PROMPT1_ID=your-sheet-id-here
GOOGLE_SHEET_PROMPT2_ID=your-sheet-id-here
```

**3. Get Sheet ID:**
- Create a Google Sheet
- Copy ID from URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
- Share sheet with service account email (in JSON file)

### Usage

**Quick test:**
```bash
python test_sheets_quick.py
```

**In your code:**
```python
from notes_agent.tools_sheets import write_triage_items_to_sheet
import os

url = write_triage_items_to_sheet(
    items=triage_items,
    sheet_id=os.getenv('GOOGLE_SHEET_PROMPT1_ID'),
    clear_existing=True  # or False to append
)
```

### Output Format

Google Sheet columns:
- ID (T001, T002, etc.)
- Date (YYYY-MM-DD)
- Personal/Work
- Domain
- Type (Task, Observation, etc.)
- Tags (comma-separated)
- Niche Signal (TRUE/FALSE)
- Publishable (TRUE/FALSE)
- Raw Context (verbatim text)

**Why Google Sheets for testing:**
- ✅ Easy to review and compare results visually
- ✅ Share with non-technical stakeholders
- ✅ Quick filtering/sorting for pattern analysis
- ✅ No database setup needed for intermediate testing

---

## LLM-as-Judge Evaluation

### Overview

We use **GPT-4 as an evaluator** to objectively compare prompt variants. The evaluator assesses 6 dimensions of triage quality on a 1-5 scale.

### Evaluation Criteria

1. **Completeness (1-5)** - Did it extract ALL meaningful items?
2. **Classification Accuracy (1-5)** - Are types/domains correct?
3. **Granularity (1-5)** - Right level of detail (not too broad/narrow)?
4. **Tag Quality (1-5)** - Relevant, specific keywords?
5. **Niche Signal Accuracy (1-5)** - Correct behavioral pattern assessment?
6. **Publishability Accuracy (1-5)** - Correct content potential assessment?

**Overall Score:** Average across all dimensions

### Usage

**Single Evaluation:**
```bash
cd triage-agent-prompt1/agents/triage-agent
python scripts/evaluate_prompts.py --input tests/inputs/sample_01.txt
```

**Compare Two Prompts:**
```bash
# First, save outputs from both worktrees
cd triage-agent-prompt1/agents/triage-agent
python scripts/test_layer1.py  # Saves to tests/output_layer1.json

cd triage-agent-prompt2/agents/triage-agent
python scripts/test_layer1.py  # Saves to tests/output_layer1.json

# Then compare
python scripts/evaluate_prompts.py \
  --input tests/inputs/sample_01.txt \
  --compare \
  --prompt1-output triage-agent-prompt1/tests/output_layer1.json \
  --prompt2-output triage-agent-prompt2/tests/output_layer1.json
```

### Evaluation Output

**Console:**
```
COMPARING PROMPTS: prompt1 vs prompt2
================================================================================

prompt1:
  Overall Score: 4.2/5.0
  Items: 8
  Recommendation: keep
  Strengths: Excellent granularity, captures all items
  Weaknesses: Tags could be more specific

prompt2:
  Overall Score: 3.8/5.0
  Items: 6
  Recommendation: revise
  Strengths: Good classification accuracy
  Weaknesses: Missed 2 items, granularity too broad

🏆 Winner: prompt1
```

**Google Sheets (optional):**
```python
from notes_agent.evaluator import evaluate_triage_output
from notes_agent.tools_sheets import write_evaluation_to_sheet

evaluation = evaluate_triage_output(input_text, items, "prompt1")
write_evaluation_to_sheet(evaluation, sheet_id, worksheet_name="Evaluation")
```

Creates an "Evaluation" tab with:
- Summary row (overall score, recommendation, strengths/weaknesses)
- Per-item scores for all 6 dimensions
- Color-coded overall score (red <3, yellow 3-4, green 4+)

### Evaluation Workflow

**Complete Flow:**
```bash
# 1. Test both prompts in parallel worktrees
Terminal 1: cd triage-agent-prompt1/agents/triage-agent && python test_sheets_quick.py
Terminal 2: cd triage-agent-prompt2/agents/triage-agent && python test_sheets_quick.py

# 2. Run evaluation
python scripts/evaluate_prompts.py --compare \
  --input tests/inputs/sample_01.txt \
  --prompt1-output path/to/prompt1_output.json \
  --prompt2-output path/to/prompt2_output.json

# 3. Review results in console + Google Sheets

# 4. Keep the winner
# If prompt1 wins, merge test/prompt1 to master
git checkout master
git merge test/prompt1
git push

# 5. Clean up
git worktree remove triage-agent-prompt1
git worktree remove triage-agent-prompt2
git branch -d test/prompt1 test/prompt2
```

### Why LLM-as-Judge?

- **Objective**: Consistent evaluation criteria
- **Fast**: Evaluate in seconds, not hours
- **Scalable**: Test 10+ variants easily
- **Detailed**: Get per-item feedback
- **Cost-effective**: ~$0.01 per evaluation with GPT-4o

**Limitations:**
- Evaluator can be wrong (validate with manual review)
- Works best with clear evaluation criteria
- Needs good examples in evaluator prompt

---

## Deployment

### Local Testing
```bash
python scripts/run_pipeline.py --limit 1
```

### VPS Deployment (24/7 Automation)

**1. Deploy Code:**
```bash
# SSH to VPS
ssh user@vps-ip

# Clone repo
cd /home/your-user/
git clone <repo-url> notes-agent
cd notes-agent

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add .env
nano .env  # Paste credentials

# Test
python scripts/run_pipeline.py --limit 1
```

**2. Set Up Cron:**
```bash
crontab -e

# Run every hour
0 * * * * cd /home/your-user/notes-agent && /home/your-user/notes-agent/venv/bin/python scripts/run_pipeline.py >> logs/cron.log 2>&1
```

**3. Monitor:**
```bash
tail -f logs/cron.log
tail -f logs/decisions_*.jsonl
```

---

## Bugs Found & Lessons Learned

### Bug #1: Claude API Returns Malformed JSON

**Problem:** When using Anthropic's API to generate JSON, Claude wraps the JSON in explanatory text ("Here is the JSON...") and often truncates mid-response, causing `JSONDecodeError`.

**Root Cause:**
1. Claude adds conversational preamble before JSON
2. `max_tokens` was too low (1200), causing JSON to be cut off mid-object
3. No enforcement of valid JSON structure in Anthropic Python SDK

**Attempted Fixes:**
- Regex extraction of JSON from explanatory text → Still got truncated/malformed JSON
- Increasing `max_tokens` → Helped but didn't guarantee valid JSON
- Adding "respond ONLY with JSON" to prompt → Claude still added text wrapper

**Solution:** Use OpenAI's API with `response_format={"type": "json_object"}`.

```python
from openai import OpenAI

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},  # Guarantees valid JSON
    messages=[...]
)

data = json.loads(resp.choices[0].message.content)  # Always works
```

**Lesson:** When you need structured JSON output, use OpenAI's `response_format` parameter. Don't rely on prompt engineering alone.

---

### Bug #2: Notion API Changed - No `databases.query()` Method

**Problem:** Code used `notion.databases.query()` but notion-client 2.7.0 doesn't expose this method.

**Root Cause:** Notion API evolved. The Python SDK doesn't wrap all endpoints consistently.

**Solution:** Use direct HTTP requests via `httpx` instead of relying on SDK methods.

```python
import httpx

url = f'https://api.notion.com/v1/databases/{database_id}/query'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}
response = httpx.post(url, headers=headers, json=body)
```

**Lesson:** When SDK doesn't expose needed functionality, use direct HTTP requests. APIs are more stable than SDK wrappers.

---

### Bug #3: Supabase Schema Mismatch

**Problem:** Code tried to insert `block_id` (string) but database expected `block_number` (integer).

**Root Cause:** Database schema evolved but code wasn't updated.

**Solution:**
1. Check actual database columns: `SELECT * FROM table LIMIT 1`
2. Match code to database, not assumptions
3. Extract block number from block_id: `int(block_id.replace("b", ""))`

**Lesson:** Always verify database schema before assuming structure. Schema is source of truth, not code comments.

---

## Learning Path (What We Built)

### Week 1: Agent 1 - The Classifier ✅

**Concept:** Deterministic control flow with LLM as reasoning module

**What we built:**
- Two-phase LLM pipeline (split → classify)
- Pydantic validation for all LLM outputs
- Confidence threshold enforcement
- Idempotency via Supabase tracking
- Complete observability (JSONL logs)

**Key learnings:**
- LLM = function, not OS
- Python controls the loop
- Never trust raw LLM output
- Observability is non-negotiable
- Prompts are code (version control them)

---

## What We Didn't Build (And Why)

### Agent 2: The Researcher (Explored but Not Deployed)

**Concept:** Autonomous agent with tool calling (LLM controls the loop)

**What we prototyped:**
- Agent loop: Perceive → Reason → Act → Observe
- Multiple tools (query_journal, search_web, fetch_url)
- LLM decides which tools to use and when to stop
- Conversation memory management

**Why not deployed:**
- Not needed for current use case (simple pipeline works)
- Added complexity without benefit
- Cost implications (multiple LLM calls per query)
- Current pipeline is deterministic and reliable

**When to use Agent 2 pattern:**
- User asks varied questions (need adaptive strategy)
- Task requires combining multiple data sources
- Don't know exact steps ahead of time

### Agent 3: Memory/RAG (Explored Conceptually)

**Concept:** Long-term memory via vector database

**What RAG does:**
1. Store past conversations with embeddings
2. Search by semantic similarity
3. Inject relevant memories into prompt
4. LLM "remembers" via context

**Why not deployed:**
- Current pipeline doesn't need conversation history
- Each entry processed independently
- No multi-turn interactions with user

**When to use RAG:**
- Build a chat interface over your data
- Need to reference past analyses
- User asks "What did we discuss about X?"

---

## Prompt Engineering Principles

### 1. Prompts Are Code

**Store as `.txt` files:**
- `prompts/block_splitter_system.txt`
- `prompts/block_classifier_system.txt`

**Why:**
- Version control
- Easy to edit without touching code
- Can A/B test different prompts
- Changes take effect immediately

### 2. Be Explicit About Schema

**Include exact JSON structure in prompt:**
```
Output must be valid JSON with this structure:
{
  "blocks": [
    {
      "block_id": "b1",
      "block_name": "2-6 word name",
      "block_text": "full text content"
    }
  ]
}
```

### 3. Provide Examples

**Show the LLM what you want:**
```
Example input:
"I'm worried about money again. Need to check my budget but avoiding it."

Example output:
{
  "block_id": "b1",
  "core_emotion": "anxiety",
  "themes": ["money", "avoidance", "budget"],
  "behavioral_response": "avoid",
  ...
}
```

### 4. Confidence is Key

**Always ask LLM for confidence:**
```
"confidence": 0.85  // How certain are you? (0.0-1.0)
```

**Use it to filter:**
```python
if classification.confidence >= 0.7:
    save_to_database(classification)
else:
    log_skipped(classification, "confidence_too_low")
```

---

## Production Checklist

**Before deploying:**
- [ ] All API keys in `.env` (not hardcoded)
- [ ] `.env` in `.gitignore`
- [ ] Supabase schema created
- [ ] Test run: `python scripts/run_pipeline.py --limit 1`
- [ ] Logs directory exists
- [ ] Cron job tested locally
- [ ] Monitor first few runs

**Security:**
- [ ] `.env` has `chmod 600` (VPS)
- [ ] No secrets committed to Git
- [ ] SSH key authentication (not passwords)

---

## Future Enhancements (Not Implemented)

### 1. Real-Time Processing
- Set up Notion webhook (when available)
- Process entries immediately on creation

### 2. Better Classification
- Fine-tune model on your journal data
- Add domain-specific emotion categories
- Multi-label themes (not just keywords)

### 3. Pattern Analysis
- Weekly summaries of emotional trends
- Trigger detection (what causes anxiety?)
- Behavioral intervention suggestions

### 4. Query Interface
- Natural language queries over classified data
- "Show me times I felt anxious about money"
- Build Agent 2 (Researcher) for this

---

## Cost Analysis

**Current monthly costs:**
- OpenAI API: ~$1-5 (depending on journal volume)
- Supabase: $0 (free tier)
- Notion API: $0 (free)
- VPS: Already owned

**Optimization opportunities:**
- Use `gpt-4o-mini` instead of `gpt-4o` (10x cheaper)
- Batch process entries (fewer API calls)
- Cache classification prompts

---

## Conclusion

**What we built:** A production-ready, autonomous journal classification system.

**Key achievement:** Transformed unstructured journal entries into queryable psychological data.

**Architecture pattern:** Deterministic pipeline with LLM as reasoning module.

**Next steps:** Deploy to VPS with cron job for 24/7 automation.

**Most important lesson:** LLM is a tool, not magic. Build observable, maintainable systems around it.
