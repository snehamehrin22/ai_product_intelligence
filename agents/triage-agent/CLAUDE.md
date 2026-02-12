# Triage Agent - Brain Dump Processor

## Project Overview

**Problem:** Stream-of-consciousness brain dumps are unstructured and contain mixed types of information (tasks, observations, ideas, questions).

**Solution:** An AI triage agent that automatically processes raw brain dumps and classifies them into atomic, actionable items with metadata.

**Goal:** Transform raw text into structured triage items with:
- Clear type classification (Task, Observation, Insight, Question, etc.)
- Personal/Work domain categorization
- Specific domain tags (product, engineering, health, etc.)
- Thematic tags for pattern detection
- Niche signal detection (behavioral patterns worth sharing)
- Publishability assessment (content creation potential)

---

## System Architecture (Current)

### The Pipeline

```
Raw Brain Dump Text
        ↓
Layer 1: Triage Agent (LLM)
  - Split into atomic items
  - Classify each item
  - Extract metadata
        ↓
Pydantic Validation (TriageItem schema)
        ↓
Output to Google Sheets
        ↓
Optional: LLM-as-Judge Evaluation
```

### File Structure

```
triage-agent/
├── src/notes_agent/              # Main pipeline
│   ├── layer1_triage.py          # Core triage logic
│   ├── llm_clients.py            # DeepSeek API integration
│   ├── schemas.py                # Pydantic models (source of truth)
│   ├── tools_sheets.py           # Google Sheets output
│   └── evaluator.py              # LLM-as-judge evaluation
│
├── prompts/                      # LLM prompts (version controlled)
│   ├── layer1_triage_system.txt  # Main triage prompt
│   └── evaluator_system.txt      # Evaluation criteria
│
├── scripts/                      # Executable scripts
│   ├── test_layer1.py            # Main test runner
│   ├── run_triage_with_eval.py   # Complete workflow + eval
│   └── evaluate_prompts.py       # Compare prompt variants
│
├── tests/inputs/                 # Test data
│   ├── sample_01.txt
│   └── sample_02.txt
│
├── config/
│   └── google_service_account.json  # Google Sheets credentials
│
└── logs/                         # Runtime logs
```

---

## Core Principles

### 1. LLM = Reasoning Module, NOT the OS

**Current Pattern:**
```python
# Single LLM call does end-to-end triage
raw_text = "I need to fix the bug in the login flow. Also wondering if we should pivot to AI products..."

items = triage_braindump(raw_text)
# Returns: [
#   TriageItem(type="Task", domain="engineering", text="fix bug in login flow"),
#   TriageItem(type="Question", domain="product", text="should we pivot to AI products?")
# ]
```

**Key Insight:** LLM does the reasoning (classification), Python validates with Pydantic.

### 2. Never Trust Raw LLM Output

**Always use Pydantic for validation:**
```python
# ❌ Bad
items = json.loads(llm_response)  # What if LLM returns invalid data?

# ✅ Good
items = [TriageItem(**item) for item in json.loads(llm_response)]  # Pydantic validates
```

**Why:** LLMs are probabilistic. They occasionally return:
- Missing required fields
- Wrong data types
- Values outside expected ranges

Pydantic catches these before they corrupt your data.

### 3. Clean Separation of Concerns

**Modules have ONE job:**
- `schemas.py` - Data structures (Pydantic models)
- `layer1_triage.py` - LLM triage logic ONLY
- `llm_clients.py` - API calls ONLY (DeepSeek)
- `tools_sheets.py` - External I/O ONLY (Google Sheets)
- `evaluator.py` - Quality assessment ONLY

**No mixing:** LLM code doesn't touch Google Sheets. Output code doesn't do validation.

---

## Triage Schema

### TriageItem Fields

**Required:**
- `id`: str - Unique identifier (e.g., "T001", "T002")
- `date`: str - Date in YYYY-MM-DD format
- `personal_or_work`: str - Either "Personal" or "Work"
- `domain`: str - Specific domain (product, engineering, health, etc.)
- `type`: str - Item type (Task, Observation, Insight, Question, etc.)
- `tags`: List[str] - 3-6 keyword tags
- `niche_signal`: bool - Is this a behavioral pattern worth sharing?
- `publishable`: bool - Does this have content creation potential?
- `raw_context`: str - Verbatim text from original input

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

## Usage

### Quick Test

```bash
# Test with all sample inputs
python scripts/test_layer1.py

# Complete workflow: triage + sheets + evaluation
python scripts/run_triage_with_eval.py \
  --input tests/inputs/sample_01.txt \
  --prompt-version "v1.0" \
  --sheet-id YOUR_SHEET_ID
```

### Testing Workflow

1. **Add test samples** to `tests/inputs/sample_XX.txt`
2. **Run triage**: `python scripts/test_layer1.py`
3. **Review output** in console or Google Sheets
4. **Evaluate quality** with `run_triage_with_eval.py`
5. **Iterate on prompt** in `prompts/layer1_triage_system.txt`

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

## Architecture Evolution

### What We Built

**Layer 1: Triage Agent** ✅
- Single LLM call for end-to-end classification
- Pydantic validation for all outputs
- Google Sheets integration for easy review
- LLM-as-judge evaluation for prompt testing

**Key learnings:**
- Simplicity wins: single-pass classification beats multi-stage pipelines
- Validation is critical: Pydantic catches LLM errors
- Cheap models work: DeepSeek is 10-20x cheaper than GPT-4, good enough for structured tasks
- Prompts are code: version control them, A/B test them

### What's Next

**Layer 2: Smart Routing** (Planned)
- Route triage items to appropriate systems
  - Tasks → Task manager (Linear, Notion, etc.)
  - Insights → Knowledge base
  - Questions → Research queue
- Add confidence scores for routing decisions
- Track completion status

**Layer 3: Pattern Detection** (Future)
- Analyze triage history for recurring themes
- Detect behavioral patterns worth sharing
- Suggest content ideas based on niche signals
- Weekly summaries of activity patterns

---

## Prompt Engineering Principles

### 1. Prompts Are Code

**Store as `.txt` files:**
- `prompts/layer1_triage_system.txt` - Main triage prompt
- `prompts/evaluator_system.txt` - Evaluation criteria

**Why:**
- Version control
- Easy to edit without touching code
- Can A/B test different prompts
- Changes take effect immediately

### 2. Be Explicit About Schema

**Include exact JSON structure in prompt:**
```json
[
  {
    "id": "T001",
    "date": "2024-02-11",
    "personal_or_work": "Work",
    "domain": "product",
    "type": "Task",
    "tags": ["bug-fix", "authentication"],
    "niche_signal": false,
    "publishable": false,
    "raw_context": "fix bug in login flow"
  }
]
```

### 3. Provide Examples

**Show the LLM what you want in the prompt itself.** The current `layer1_triage_system.txt` includes detailed examples of:
- Different item types (Task, Observation, Insight, Question)
- Edge cases (ambiguous items, multiple items in one sentence)
- What qualifies as "niche signal" vs not
- What's publishable vs not

---

## Setup Checklist

**Initial Setup:**
- [ ] Create virtual environment: `python3.13 -m venv .venv`
- [ ] Activate: `source .venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Add API keys to `.env` (DEEPSEEK_API_KEY, OPENAI_API_KEY, GOOGLE_SHEET_PROMPT1_ID)
- [ ] Add Google service account JSON to `config/`
- [ ] Test run: `python scripts/test_layer1.py`

**Security:**
- [ ] `.env` in `.gitignore` (already there)
- [ ] `config/google_service_account.json` in `.gitignore` (already there)
- [ ] No secrets committed to Git

---

## Cost Analysis

**Current costs per brain dump:**
- DeepSeek API: ~$0.001-0.003 per triage (ultra cheap)
- OpenAI API (for evaluation): ~$0.01 per eval (optional)
- Google Sheets: $0 (free)

**Why DeepSeek:**
- 10-20x cheaper than GPT-4
- Good enough for structured classification tasks
- Fast response times

---

## Next Steps

**Immediate:**
- [ ] Integrate with daily workflow (manual or automated input)
- [ ] Build dashboard to visualize triage patterns over time
- [ ] Add Layer 2: Smart routing (tasks → task manager, insights → knowledge base)

**Future:**
- [ ] Fine-tune model on your triage data for better accuracy
- [ ] Add semantic search over past triage items
- [ ] Build query interface ("show me all product insights from last month")
