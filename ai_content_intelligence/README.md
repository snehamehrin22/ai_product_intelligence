# AI Content Intelligence: Carousel Pipeline

Automated content creation system that transforms product research into publication-ready LinkedIn/Instagram carousels. Built on content pillars, voice profiles, and two-stage AI generation (Claude for patterns, ChatGPT for prose).

## 🎯 What This Does

**Input:** Product research markdown (from Obsidian)
**Output:** Publication-ready carousel (10 slides) in your voice
**Time:** ~15-20 minutes (down from 90 minutes manual)

## 📊 Pipeline Architecture

```
Obsidian Research
    ↓
Framework Analysis (Claude)
    ↓ [Review + Feedback]
Select Carousel Angle
    ↓
Draft Generation (Claude) - Pattern recognition
    ↓ [Review + Feedback]
Prose Tightening (ChatGPT) - Voice matching
    ↓ [Review + Feedback]
Publication-Ready Carousel
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Add your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-proj-...
```

### 2. Run Interactive Pipeline

```bash
python scripts/interactive_carousel_pipeline.py "/path/to/research.md"
```

**Example:**
```bash
python scripts/interactive_carousel_pipeline.py \
  "/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Content/Research/App Research/eight_sleep.md"
```

### 3. Workflow Steps

The CLI will guide you through:

1. **Framework Analysis** - Applies Growth Loops framework to research
   - Review: Key insights, growth loops, behavioral shifts, carousel angles
   - Feedback: Quality rating, approval, issues

2. **Angle Selection** - Choose which carousel angle to develop (1-3 options)

3. **Carousel Generation** - Two-stage AI generation
   - Stage 1 (Claude): Pattern-driven draft
   - Stage 2 (ChatGPT): Voice-matched prose
   - Review: Full 10-slide carousel preview

4. **Final Review** - Rate success, mark for publication

### 4. Output Files

All outputs saved to `data/`:

```
data/
├── analysis_outputs/
│   └── eight_sleep_framework_analysis.json
├── carousel_outputs/
│   └── eight_sleep_carousel.json
└── feedback/
    └── eight_sleep_20260206_143022.json
```

## 📚 Core Components

### Voice Profile (`config/voice_profile.json`)

Extracted from 10 carousel samples. Defines:
- **Hook patterns** (personal observation, behavioral contradiction, etc.)
- **Tone markers** (pronoun usage, sentence structure, punctuation)
- **Structural patterns** (slide count, CTA style)

**Rebuild voice profile:**
```bash
python scripts/build_voice_profile.py
```

### Author Context (`config/author_context.json`)

Personal context for authentic voice:
- Identity (pattern recognizer, freedom absolutist, etc.)
- Expertise (product analytics, behavioral science)
- Thinking patterns (observation-first, cross-domain synthesis)
- Values (freedom/autonomy, experimentation)
- Communication style (raw, specific, no jargon)

### Content Pillars (`config/content_pillars.json`)

Currently configured:
1. **Growth Loops Are Changing** - How AI transforms product growth mechanics

**Framework:** `prompts/frameworks/growth_loops_teardown_framework.md`

### Prompts

- `prompts/content_draft_claude_system.txt` - Stage 1: Claude pattern draft
- `prompts/writing_style_system.txt` - Stage 2: ChatGPT prose tightening
- `prompts/voice_analysis_system.txt` - Voice profile extraction
- `prompts/frameworks/` - Framework templates per pillar

## 🔧 Advanced Usage

### Run Steps Independently

**Framework analysis only:**
```bash
python scripts/analyze_research.py "/path/to/research.md"
```

**Carousel generation from existing analysis:**
```bash
python scripts/generate_carousel.py \
  "data/analysis_outputs/eight_sleep_framework_analysis.json" \
  1  # Angle number (1, 2, or 3)
```

### View Feedback Analytics

```bash
python scripts/view_feedback_report.py
```

Shows:
- Overall metrics (publish rate, avg success, avg time)
- Step performance (approval rates, quality ratings)
- Pillar performance (which pillars work best)
- Improvement areas (recurring issues, prompt updates needed)

## 📖 Schemas (Pydantic Models)

All data structures defined in `src/carousel_pipeline/schemas.py`:

- **VoiceProfile** - Voice patterns extracted from training
- **FrameworkAnalysis** - Structured analysis output
- **CarouselContent** - Complete carousel (hook, slides, CTA)
- **CarouselSlide** - Individual slide
- **StepFeedback** - Feedback per pipeline step
- **CarouselFeedback** - Complete session feedback
- **ContentPillar** - Pillar definition

## 📁 Project Structure

```
.
├── config/                     # Configuration files
│   ├── voice_profile.json      # Voice patterns (auto-generated)
│   ├── author_context.json     # Personal context
│   └── content_pillars.json    # Content pillar definitions
│
├── prompts/                    # LLM prompts (version controlled)
│   ├── content_draft_claude_system.txt
│   ├── writing_style_system.txt
│   ├── voice_analysis_system.txt
│   └── frameworks/
│       └── growth_loops_teardown_framework.md
│
├── data/                       # Generated outputs (gitignored)
│   ├── training_carousels/     # Voice training samples
│   ├── analysis_outputs/       # Framework analyses
│   ├── carousel_outputs/       # Generated carousels
│   └── feedback/               # Session feedback
│
├── src/carousel_pipeline/      # Core modules
│   ├── schemas.py              # Pydantic models (SINGLE SOURCE OF TRUTH)
│   ├── voice_profile.py        # Voice extraction
│   ├── framework_analyzer.py   # Framework application
│   ├── carousel_generator.py   # Two-stage generation
│   └── feedback_analyzer.py    # Feedback analytics
│
└── scripts/                    # Executable scripts
    ├── interactive_carousel_pipeline.py  # Main CLI
    ├── analyze_research.py               # Framework analysis only
    ├── generate_carousel.py              # Generation only
    ├── build_voice_profile.py            # Voice profile builder
    └── view_feedback_report.py           # Feedback analytics
```

## 🎨 Two-Stage Generation Philosophy

**Why Claude + ChatGPT?**

1. **Stage 1 (Claude):** Better at pattern recognition and cross-domain synthesis
   - Identifies behavioral patterns in research
   - Maps to content pillar frameworks
   - Applies author's thinking patterns
   - Generates insight-driven structure

2. **Stage 2 (ChatGPT):** Better at consistent prose and voice matching
   - Tightens sentence structure (avg 3-6 words)
   - Matches voice profile patterns
   - Applies tone markers
   - Ensures readability

**Result:** Carousels with deep insights AND authentic voice.

## 📈 Future Enhancements

Currently focusing on **Growth Loops** pillar. Planned:

- [ ] Add 2 more content pillars (targeting 3 total)
- [ ] Multi-pillar analysis (1 research → 3 carousels)
- [ ] AI-suggested angles (beyond framework-defined angles)
- [ ] Automated design generation (Figma/Canva templates)
- [ ] Prompt auto-improvement from feedback patterns
- [ ] Voice confidence scoring per carousel

## 🔍 Testing

Test inputs in `tests/inputs/` (not yet created - add your test research files here).

**Recommended test cases:**
- Basic happy path (strong research, clear patterns)
- Sparse research (limited data points)
- Multi-product comparison research
- Edge case topics (outside normal domain)

## 🐛 Known Issues

None yet - first version just built!

## 📝 Feedback Loop

Every session captures:
- Quality ratings per step (1-5)
- Approval decisions
- Specific issues identified
- What was wrong/missing
- Time to complete

Use feedback reports to:
- Identify weak pipeline steps
- Find recurring issues
- Update prompts systematically
- Measure improvement over time

## 🤝 Contributing

To add a new content pillar:

1. **Define pillar** in `config/content_pillars.json`:
   - pillar_id, name, thesis
   - Behavioral shifts
   - Keywords for matching

2. **Create framework template** in `prompts/frameworks/`:
   - Analysis structure
   - Output requirements
   - Carousel angle guidance

3. **Test with research:**
   - Run through interactive pipeline
   - Capture feedback
   - Iterate on framework

## 📄 License

Private project - not for public distribution.

---

**Questions?** Check the code comments or run scripts with `--help` flag.
