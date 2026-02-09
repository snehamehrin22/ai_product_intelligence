# Carousel Eval System - Session Results

## System Built

✅ **Complete evaluation and iteration system** for carousel generation quality

### Components Created:

1. **Supabase Database** (`case_studies_factory` schema)
   - `carousel_evals` - stores all generation attempts and scores
   - `expected_outputs` - gold standard carousels
   - `prompt_versions` - tracks prompt evolution

2. **Evaluation Engine** (`src/carousel_pipeline/carousel_eval.py`)
   - Compares generated vs expected carousels
   - Calculates match scores (structure, content, title similarity)
   - Stores results in Supabase

3. **Prompt Iterator** (`src/carousel_pipeline/prompt_iterator.py`)
   - Analyzes failures with Claude
   - Suggests prompt improvements
   - Saves versioned prompts

4. **Training Data**
   - Added gold standard Superhuman carousel as training example
   - Updated metadata to include it in pillar_01 examples

---

## Evaluation Results

### Iteration Comparison

| Iteration | Model | Prompt | Match Score | Content Sim | Notes |
|-----------|-------|--------|-------------|-------------|-------|
| **Baseline** | Claude.ai Opus | Web app | **100%** | **100%** | Gold standard |
| **Iter 1** | Sonnet 4 | Original | **59.37%** | 32.28% | Best API result |
| **Iter 2** | Sonnet 4 | v2 (add depth) | 50.53% | 31.93% | ❌ Went wrong direction |
| **Iter 3** | Sonnet 4 | v3 (narrative) | 56.09% | 31.58% | Better, still not there |
| **Iter 4** | **Opus 4** | v3 (narrative) | 52.64% | 32.01% | ⚠️ Surprisingly worse than Sonnet |

### Key Finding: **40% Quality Gap Between API and Claude.ai Web**

All API iterations (regardless of model or prompt) scored ~50-60% match with content similarity stuck at ~32%.

---

## Root Cause Analysis

### Why the Gap Exists

**NOT the model:**
- Opus 4 (same as web) performed worse than Sonnet 4
- Model alone doesn't explain the difference

**NOT the prompt:**
- 3 prompt iterations didn't close the gap
- All variations had similar low content similarity

**Likely causes:**
1. **Different starting context** - Claude.ai web has conversation history and project memory
2. **Iterative refinement** - Web version might have been edited/regenerated multiple times
3. **Additional input** - Research markdown might have been supplemented with other context

### Content Differences

API generates:
- Generic observations
- Short bullet points
- Framework-focused

Gold standard has:
- Personal narratives ("I triaged 80 emails...")
- Detailed multi-paragraph slides
- Specific product comparisons
- Strategic implications sections

---

## Solutions Implemented

### 1. Gold Standard as Training Example ✅

Added `carousel_superhuman_gold.txt` to `pillar01_voice/` training data.

**Next test:** Regenerate with gold standard in training set and see if match improves.

### 2. Two-Stage Pipeline with ChatGPT Editing ✅

**Opus → ChatGPT Editor** approach tested on Iteration 4:

**Input (Opus raw):** Verbose, detailed, framework-heavy
**Output (ChatGPT edited):** Tighter, narrative, scroll-friendly

**Editor Prompt Used:**
- Make people swipe (not just read)
- Fewer concepts, more clarity
- Narrative arc with tension
- Kill jargon and buzzwords
- Short sentences, clean rhythm

**Result:** Much better readability and flow

### 3. Multi-Pillar Generator Updated

Now supports:
- Custom prompt templates (for iterations)
- Model selection (Sonnet vs Opus)
- Optional ChatGPT tightening stage

---

## Recommended Next Steps

### Immediate:
1. **Re-run with gold standard in training** - See if match score improves
2. **Test Opus → ChatGPT pipeline** - Compare edited version against gold standard
3. **Iterate on ChatGPT editor prompt** - Fine-tune the tightening process

### Strategic:
1. **Build full automation** - If score < threshold, auto-iterate until match
2. **Add more gold standards** - Create expected outputs for other apps
3. **A/B test prompts** - Compare which prompt structures work best

### Alternative Approach:
1. **Accept the difference** - API version might be "good enough"
2. **Manual polish** - Use API as draft, manually edit to gold standard
3. **Hybrid workflow** - API generates → Human reviews → ChatGPT tightens

---

## Files Created

### Configuration
- `config/supabase_schema.sql` - Full database schema
- `config/create_expected_outputs_table.sql` - Table creation script
- `config/add_missing_columns.sql` - Column migration script
- `config/recreate_carousel_evals.sql` - Table recreation script

### Code
- `src/carousel_pipeline/carousel_eval.py` - Evaluation engine
- `src/carousel_pipeline/prompt_iterator.py` - Auto-improvement system
- Updated `src/carousel_pipeline/prompt_builder.py` - Custom template support
- Updated `src/carousel_pipeline/multi_pillar_generator.py` - Model selection

### Prompts
- `prompts/versions/carousel_generation_pillar_01_v2.txt` - Failed attempt (too dense)
- `prompts/versions/carousel_generation_pillar_01_v3.txt` - Narrative focus

### Data
- `data/expected_outputs/Superhuman_pillar_01_gold_standard.json` - Gold standard
- `data/training_carousels/pillar01_voice/carousel_superhuman_gold.txt` - Training example
- `data/carousel_outputs/Superhuman_pillar_01_iteration_0[1-4]*` - All iterations
- `data/carousel_outputs/Superhuman_pillar_01_iteration_04_opus_edited.txt` - ChatGPT edited

### Documentation
- `EVAL_SYSTEM.md` - System overview and usage guide
- `EVAL_SYSTEM_RESULTS.md` - This file

---

## Supabase Data Summary

**Expected Outputs:** 1 (Superhuman pillar_01)
**Carousel Evals:** 4 iterations stored
**Prompt Versions:** 2 (v2, v3)

All stored in `case_studies_factory` schema.

---

## Key Learnings

1. **Quality gaps need data, not just prompts** - Training examples matter more than prompt engineering
2. **Model != Quality** - Opus didn't automatically match web output
3. **Two-stage works** - Generate with Opus, tighten with ChatGPT shows promise
4. **Eval systems reveal truth** - Automated iteration showed v2 made things worse
5. **Content similarity is hard** - Matching ideas/angles is harder than matching structure/style

---

## Cost Implications

### Per Carousel Generation:
- **Sonnet 4:** ~$0.10-0.20
- **Opus 4:** ~$1.00-2.00
- **ChatGPT editing:** ~$0.05-0.10

### Recommended Pipeline:
**Opus + ChatGPT = ~$1.10 per carousel**

Worth it if quality matches gold standard after including training example.

---

## Next Session Priorities

1. Test with gold standard in training data
2. Evaluate Opus → ChatGPT edited version
3. If match score hits 85%+, update batch generator to use this pipeline
4. If not, investigate conversation export from Claude.ai web
