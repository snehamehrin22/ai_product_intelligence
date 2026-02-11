# Carousel Evaluation System

Automated prompt iteration system that compares generated carousels against expected outputs and improves prompts until they match.

---

## 🎯 Overview

**Problem**: Generated carousels might not match your exact style/expectations
**Solution**: Store expected outputs → Generate → Compare → Iterate prompts automatically

**Flow**:
```
Expected Output (gold standard)
    ↓
Generate Carousel (Claude)
    ↓
Compare (match score)
    ↓
If score < threshold:
  → Analyze failures (Claude)
  → Adjust prompt automatically
  → Generate again
    ↓
Repeat until approved or max iterations
```

---

## 📊 Components

### 1. **Supabase Tables**

**`carousel_evals`** - Stores each generation attempt
- Input: research file, pillar, expected output
- Output: generated carousel, match score, differences
- Iteration tracking: parent/child eval IDs

**`prompt_versions`** - Tracks prompt evolution
- Per-pillar prompt versions
- Performance metrics (avg match score, approval rate)

**`expected_outputs`** - Gold standard carousels
- One per research file + pillar combination
- Source tracking (manual, approved, etc.)

### 2. **Comparison Engine**

`src/carousel_pipeline/carousel_eval.py`

**Metrics**:
- **Structure match** (0-1): Slide count, titles
- **Content similarity** (0-1): Semantic similarity per slide
- **Style match** (0-1): Tone, length, format

**Overall match score**: Weighted average
```python
match_score = (
    structure_match * 0.2 +
    content_similarity * 0.6 +
    style_match * 0.2
)
```

### 3. **Prompt Iterator**

`src/carousel_pipeline/prompt_iterator.py`

**Auto-improvement flow**:
1. Analyze failures with Claude
2. Identify root cause
3. Suggest prompt adjustments
4. Apply adjustments
5. Save new prompt version

**Versioning**: Prompts saved to `prompts/versions/`

---

## 🚀 Quick Start

### Setup

1. **Install dependencies**:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Add Supabase credentials to `.env`**:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
```

3. **Create Supabase tables**:
```sql
-- Run the SQL in config/supabase_schema.sql in your Supabase SQL editor
```

---

## 📝 Usage

### Step 1: Store Expected Output

First, create a gold standard carousel for evaluation:

```bash
python scripts/eval_carousel.py store-expected \
  --research "Superhuman" \
  --pillar pillar_01 \
  --expected-file "/path/to/expected_carousel.json"
```

**Expected file format** (JSON):
```json
{
  "title": "Expected carousel title",
  "pillar": "pillar_01",
  "slides": [
    {
      "index": 1,
      "title": "Hook",
      "text_lines": [
        "Line 1 of slide 1",
        "Line 2 of slide 1"
      ]
    },
    {
      "index": 2,
      "title": "Setup",
      "text_lines": ["Slide 2 content"]
    }
    // ... more slides
  ]
}
```

### Step 2: Run Eval Loop

```bash
python scripts/eval_carousel.py eval \
  --research "/path/to/Superhuman.md" \
  --pillar pillar_01 \
  --max-iterations 5 \
  --threshold 0.85
```

**Parameters**:
- `--research`: Path to research markdown file
- `--pillar`: Pillar ID (`pillar_01`, `pillar_02`, `pillar_03`)
- `--max-iterations`: Max attempts before stopping (default: 5)
- `--threshold`: Target match score (default: 0.85, range: 0-1)

---

## 📈 What Happens During Eval

### Iteration 1
```
🤖 Generating carousel...
✓ Carousel generated (10 slides)

📊 Evaluating...
   Match score: 0.72
   Structure: 1.00
   Content: 0.65
   Differences: 4

   ✓ Eval stored: uuid-here

🔄 Score below threshold. Iterating prompt...
🔍 Analyzing failures...
   Root cause: Instructions too vague on slide length
   Priority: high

   Adjustments made:
     • instructions: Add constraint: "Keep each slide to 2-3 lines max"
     • constraints: Emphasize matching example density

   ✓ New prompt version saved: v2
```

### Iteration 2
```
🤖 Generating carousel (with v2 prompt)...
✓ Carousel generated (10 slides)

📊 Evaluating...
   Match score: 0.87
   Structure: 1.00
   Content: 0.85
   Differences: 1

✅ SUCCESS! Match score 0.87 >= 0.85
   Iterations needed: 2
```

---

## 🔍 Viewing Results

### In Supabase

**See all eval attempts**:
```sql
SELECT
  research_name,
  pillar_id,
  iteration,
  match_score,
  created_at
FROM carousel_evals
ORDER BY created_at DESC;
```

**See prompt evolution**:
```sql
SELECT
  pillar_id,
  version,
  avg_match_score,
  total_evals,
  approval_rate
FROM prompt_versions
ORDER BY pillar_id, version;
```

**See what's failing**:
```sql
SELECT
  research_name,
  pillar_id,
  iteration,
  match_score,
  differences
FROM carousel_evals
WHERE match_score < 0.85
ORDER BY match_score ASC;
```

---

## 🛠️ Advanced Usage

### Manual Prompt Adjustment

If auto-iteration isn't working, manually edit:

```
prompts/versions/carousel_generation_pillar_01_v3.txt
```

Then continue eval from that version.

### Custom Comparison Logic

Edit `src/carousel_pipeline/carousel_eval.py`:

```python
def evaluate_carousel(generated, expected):
    # Add custom metrics
    # Adjust weighting
    # ...
```

### Human-in-the-Loop

After auto-iteration reaches threshold, review in Supabase:

```sql
UPDATE carousel_evals
SET human_approved = true,
    human_feedback = 'Great! Approved for production'
WHERE id = 'eval-uuid-here';
```

---

## 📊 Metrics to Track

**Per Pillar**:
- Avg match score trend
- Iterations to approval
- Common failure patterns

**Overall**:
- Prompt stability (versions per pillar)
- Approval rate over time
- Most common adjustments needed

---

## 🐛 Troubleshooting

### "No expected output found"
→ Run `store-expected` command first

### Match score stuck below threshold
→ Check `differences` in Supabase
→ Review prompt versions manually
→ Consider adjusting threshold or expected output

### Rate limits hit
→ Add delays between iterations
→ Use `--max-iterations 3` instead of 5

---

## 🎯 Best Practices

1. **Start with 1-2 gold standards** per pillar
2. **Set realistic thresholds**: 0.80-0.85 is good
3. **Review auto-adjustments**: Check `prompts/versions/` after each run
4. **Track patterns**: What keeps failing? Adjust framework, not just prompts
5. **Iterate on expected outputs too**: Sometimes the gold standard needs updating

---

## 📁 File Structure

```
config/
  └── supabase_schema.sql          # DB schema

src/carousel_pipeline/
  ├── carousel_eval.py             # Comparison engine
  └── prompt_iterator.py           # Auto-improvement

scripts/
  └── eval_carousel.py             # CLI interface

prompts/
  ├── carousel_generation_system.txt  # Base template
  └── versions/                       # Iterated versions
      ├── carousel_generation_pillar_01_v2.txt
      ├── carousel_generation_pillar_01_v3.txt
      └── ...
```

---

## Next Steps

1. Store your first expected output
2. Run eval on one carousel
3. Review results in Supabase
4. Iterate until satisfied
5. Scale to more research files

Questions? Check the code comments or Supabase logs.
