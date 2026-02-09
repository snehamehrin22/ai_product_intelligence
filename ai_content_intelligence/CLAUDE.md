# Project-Specific Claude Instructions

## Project Overview

This is an **AI content intelligence system** for analyzing apps and generating LinkedIn carousel content. The system has two main pipelines:

1. **Content Generation Pipeline** (Python)
   - Analyzes app research markdown files
   - Generates 3 carousel scripts (one per pillar) using Claude/ChatGPT
   - Outputs JSON carousel data

2. **Image Generation Pipeline** (Node.js)
   - Takes JSON carousel data
   - Generates branded PPTX slides
   - Converts to Instagram-ready images

---

## Critical Learnings (Do Not Forget)

### 🚨 Always Build Eval Systems First

**Rule:** Before iterating on prompts or models, build measurement infrastructure.

**Why:** We wasted time on prompt v2 that actually made things worse (50.53% vs 59.37%). Without eval system, we were flying blind.

**Pattern:**
```python
# 1. Build eval system FIRST
def evaluate_carousel(generated, expected):
    return match_score

# 2. Establish baseline
baseline_score = evaluate_carousel(iteration_0, gold_standard)

# 3. THEN iterate
for prompt_version in [v1, v2, v3]:
    new_score = evaluate_carousel(generate(prompt_version), gold_standard)
    if new_score > baseline_score:
        print(f"✅ Improvement: {baseline_score} → {new_score}")
    else:
        print(f"❌ Worse: {baseline_score} → {new_score}")
```

**Never:** Iterate on subjective feel. Always measure.

---

### 🚨 Supabase Schema Must Be Explicit

**Rule:** Always specify schema name explicitly when using Supabase with custom schemas.

**Why:** We spent 30 minutes debugging "table not found" errors because Supabase defaults to `public` schema but our tables were in `case_studies_factory`.

**Pattern:**
```python
# ❌ Wrong - uses default 'public' schema
supabase.table("carousel_evals").select("*").execute()

# ✅ Correct - explicit schema
supabase.schema("case_studies_factory").table("carousel_evals").select("*").execute()
```

**Config:**
```python
# Store schema name in config or .env
SUPABASE_SCHEMA = "case_studies_factory"

def get_table(table_name):
    return supabase.schema(SUPABASE_SCHEMA).table(table_name)
```

---

### 🚨 Rate Limits Must Be Handled Proactively

**Rule:** Add delays and retry logic BEFORE running batch operations, not after hitting limits.

**Why:** Our batch script hit rate limits on the 3rd carousel (30,000 tokens/min limit). Pillar_03 failed and we lost progress.

**Pattern:**
```python
import time
from anthropic import RateLimitError

def call_with_rate_limiting(api_func, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return api_func(*args)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏳ Rate limited. Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise

# Batch processing with delays
for i, item in enumerate(batch):
    result = call_with_rate_limiting(generate_carousel, item)

    if i < len(batch) - 1:  # Not last item
        time.sleep(2)  # Prevent hitting limits
```

**Always check API docs for:**
- Requests per minute limit
- Tokens per minute limit
- Retry-After headers

---

### 🚨 Web App Context ≠ API Context

**Rule:** Don't expect API outputs to match web app quality, even with same model.

**Why:** We discovered Claude Opus via API scored **52.64%** vs Claude.ai web's **100%**, even with identical prompts. The gap isn't about the model.

**Root Causes:**
1. **Conversation history** - Web app has full context, API calls are isolated
2. **Project memory** - Web app accesses project knowledge base
3. **Human refinement** - Web outputs are often edited/regenerated multiple times
4. **Hidden context** - Additional context we can't see in web app

**Pattern:**
- ✅ Use API for drafting/bulk generation
- ✅ Use two-stage pipeline: API → ChatGPT editing
- ❌ Don't compare API outputs directly to manually curated examples
- ❌ Don't assume upgrading to better model will close quality gap

**Two-Stage Solution:**
```python
# Stage 1: Generate with Claude (depth & analysis)
draft = claude_api.generate(prompt)

# Stage 2: Tighten with ChatGPT (prose & narrative)
final = chatgpt_api.edit(draft, style="narrative, scroll-friendly")
```

This approach gets us from 59% → ~75% match with gold standard.

---

### 🚨 Modularize from Day One

**Rule:** Even for "quick scripts", separate concerns from line 1.

**Why:** User's original script was 500+ lines with hardcoded content. Refactoring took extra time. Starting modular would've been faster overall.

**Architecture Pattern:**
```
project/
├── config/
│   └── constants.py          # Colors, fonts, API keys
├── src/
│   ├── core/                 # Pure logic (no I/O)
│   │   ├── evaluator.py
│   │   └── scorer.py
│   ├── integrations/         # External systems
│   │   ├── supabase.py
│   │   └── anthropic_api.py
│   └── utils/                # Helpers
│       └── text_processing.py
└── scripts/
    └── run_batch.py          # CLI entry points
```

**Separation of Concerns:**
- **Config** → Constants only (colors, fonts, URLs)
- **Core** → Pure functions (testable, no side effects)
- **Integrations** → External systems (DB, APIs)
- **Scripts** → User interface (CLI, orchestration)

**Benefits:**
- Easy to test (mock integrations)
- Easy to maintain (change config without touching logic)
- Easy to extend (add new integrations without changing core)

---

### 🚨 XML Requires Escaping

**Rule:** Always escape special characters in XML content.

**Why:** Hit `ParseError: not well-formed` because of unescaped `&` in "Status & Social Proof".

**Pattern:**
```python
import xml.etree.ElementTree as ET

# ❌ Wrong - will break
xml_content = f"<title>Status & Social Proof</title>"

# ✅ Correct - escape special chars
def escape_xml(text):
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&apos;'))

xml_content = f"<title>{escape_xml(title)}</title>"

# Or use built-in
from xml.sax.saxutils import escape
xml_content = f"<title>{escape(title)}</title>"
```

---

## Project-Specific Patterns

### Carousel Generation Workflow

```bash
# Step 1: Generate carousel JSON from research
cd ai_content_intelligence
source .venv/bin/activate
python scripts/batch_generate_carousels.py --auto

# Output: data/carousel_outputs/*.json

# Step 2: Generate PPTX slides
cd carousel-image-generator
npm run generate ../data/carousel_outputs/App_pillar_01.json

# Output: data/carousel_images/App_pillar_01.pptx

# Step 3: Convert to images (requires LibreOffice + poppler)
npm run generate-images ../data/carousel_outputs/App_pillar_01.json

# Output: data/carousel_images/App_pillar_01-1.jpg, App_pillar_01-2.jpg, ...
```

### File Locations

**Input:**
- Research files: `~/Desktop/obsidian_vaults/obsidian/Content/Research/App Research/*.md`

**Configuration:**
- Training carousels: `data/training_carousels/pillar0X_voice/`
- Metadata: `config/carousel_training_metadata.json`
- Frameworks: `prompts/frameworks/*.md`
- Prompt templates: `prompts/*.txt`

**Output:**
- Carousel JSON: `data/carousel_outputs/`
- PPTX files: `data/carousel_images/`
- Final images: `data/carousel_images/*.jpg`

**Database:**
- Schema: `case_studies_factory` (NOT `public`)
- Tables: `carousel_evals`, `expected_outputs`, `prompt_versions`

---

## Supabase Connection

```python
from supabase import create_client
import os

# Always use explicit schema
SUPABASE_SCHEMA = "case_studies_factory"

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# All queries must specify schema
result = supabase.schema(SUPABASE_SCHEMA).table("carousel_evals").select("*").execute()
```

---

## Two-Stage Content Generation

```python
# Stage 1: Claude (depth)
claude_prompt = build_carousel_prompt(research, pillar_id)
draft_xml = claude_api.generate(claude_prompt, model="claude-sonnet-4")

# Stage 2: ChatGPT (tightening)
chatgpt_prompt = f"""
Make this carousel more engaging:
- Fewer concepts, more clarity
- Narrative arc with tension
- Kill jargon and buzzwords
- Short sentences, clean rhythm
- Make people swipe (not just read)

{draft_xml}
"""
final_xml = chatgpt_api.generate(chatgpt_prompt, model="gpt-4")
```

**Why this works:**
- Claude provides comprehensive analysis (but verbose)
- ChatGPT tightens prose and improves flow
- Combined output scores higher than either alone

---

## Design System (Image Generator)

### Colors
```javascript
const COLORS = {
  burgundyDeep: "3B0510",    // Background gradient start
  burgundyMid: "5A1025",     // Background gradient mid
  cream: "F4F4F1",           // Text, accents
  gold: "D4B896",            // Titles, emphasis
  clay: "E1DBD7",            // Subtle text
  warmAccent: "A0674B",      // Accent boxes
};
```

### Layout
- Slide size: 10" x 12.5" (Instagram portrait: 1080x1350px)
- Padding: 0.7" sides
- Content width: 8.6"

### Typography
- Display: Georgia (titles, bold)
- Body: Georgia (content)
- Brand: Arial (SNEHA header, tracked)

---

## Testing & Validation

### Before Committing Code

1. **Run tests:**
   ```bash
   python -m pytest tests/
   npm test  # For Node.js
   ```

2. **Check eval scores:**
   ```sql
   SELECT carousel_name, match_score, content_similarity
   FROM case_studies_factory.carousel_evals
   ORDER BY created_at DESC
   LIMIT 5;
   ```

3. **Verify PPTX output:**
   ```bash
   open data/carousel_images/latest.pptx
   ```

---

## Common Pitfalls (AVOID)

### ❌ Don't iterate without measuring
We tried 3 prompt versions blind. v2 made things worse. Wasted 2 hours.

### ❌ Don't assume API == Web quality
Opus API scored 52% vs web's 100%. Context matters more than model.

### ❌ Don't hardcode in generators
Original script had hardcoded Superhuman content. Made it useless for other apps.

### ❌ Don't ignore rate limits
Hit 30k tokens/min limit on 3rd carousel. Should've added delays upfront.

### ❌ Don't skip schema names in Supabase
"Table not found" errors ate 30 minutes. Always use `.schema("case_studies_factory")`.

---

## Success Metrics

### Carousel Quality
- **Target:** 85%+ match score vs gold standard
- **Current:** 59.37% (baseline), ~75% (with ChatGPT editing)
- **Next:** Close gap with better training examples

### Generation Speed
- **Per carousel:** ~30s (API) + ~5s (ChatGPT editing)
- **Batch (3 carousels):** ~2 minutes (with delays)

### Image Quality
- **Resolution:** 1080x1350px @ 300 DPI
- **Format:** PPTX → PDF → JPG
- **Verification:** Manual review in PowerPoint

---

## Next Time Checklist

Before starting any work session:

- [ ] Check if eval system exists (if iterating on prompts/models)
- [ ] Review rate limits for APIs we'll use
- [ ] Verify Supabase schema name
- [ ] Create modular structure (don't write monolithic scripts)
- [ ] Document as you build (not at the end)
- [ ] Test incrementally (don't wait for full build)

---

## Commands to Remember

```bash
# Generate carousels from research
python scripts/batch_generate_carousels.py --auto

# Generate images from carousels
cd carousel-image-generator
npm run generate-images <json-file>

# Check eval scores
python scripts/check_eval_scores.py

# Create session retrospective
/session-retro
```

---

## Dependencies

### Python
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Key packages:**
- `anthropic` - Claude API
- `openai` - ChatGPT API
- `supabase` - Database
- `pydantic` - Schema validation

### Node.js
```bash
cd carousel-image-generator
npm install
```

**Key packages:**
- `pptxgenjs` - PPTX generation
- `sharp` - Image processing
- `react` + `react-dom` - Icon rendering

### System Tools (for image conversion)
```bash
# macOS
brew install --cask libreoffice
brew install poppler

# Linux
sudo apt-get install libreoffice poppler-utils
```

---

## Bugs Fixed & Lessons Learned

### Bug: Supabase "Table Not Found"
**Problem:** `APIError: Could not find the table 'public.carousel_evals'`
**Root Cause:** Tables in `case_studies_factory` schema, not `public`
**Fix:** Always use `.schema("case_studies_factory")`
**Lesson:** Don't assume default schemas. Explicitly specify.

### Bug: Rate Limit on Batch Processing
**Problem:** 3rd carousel failed with `rate_limit_error`
**Root Cause:** 30k tokens/min limit, no delays between calls
**Fix:** Add `time.sleep(2)` between requests
**Lesson:** Proactive rate limiting, not reactive.

### Bug: XML Parse Error
**Problem:** `ParseError: not well-formed (invalid token)`
**Root Cause:** Unescaped `&` in "Status & Social Proof"
**Fix:** Escape special chars: `text.replace('&', '&amp;')`
**Lesson:** Always escape user content in XML/HTML.

### Bug: Opus API < Sonnet API
**Problem:** Expected Opus to score higher, scored 52% vs Sonnet's 59%
**Root Cause:** Model isn't bottleneck; context is
**Fix:** Two-stage pipeline (Opus → ChatGPT)
**Lesson:** Better model ≠ better output. Context and editing matter more.

---

## Reference Files

- **Eval System Docs:** `EVAL_SYSTEM.md`
- **Eval Results:** `EVAL_SYSTEM_RESULTS.md`
- **Image Generator Docs:** `CAROUSEL_IMAGE_GENERATOR.md`
- **Session Learnings:** `SESSION_RETROSPECTIVE_*.md`
- **PPTX Skills:** `pptx.md`, `pptxgenjs.md`

---

*Last updated: 2026-02-06*
*Key lesson: Measure before iterating. Modularize from day one. API context ≠ Web context.*
