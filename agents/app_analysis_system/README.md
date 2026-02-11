# App Analysis System

**Deep app case studies with bi-directional Knowledge Brain connection**

---

## What This System Does

Analyzes apps through **6 structured sections**, connects findings to your **200+ frameworks in Supabase**, and builds a **pattern library** over time.

### The Workflow

```
Input: App Name (e.g., "Flo Health")
       ↓
Research 6 Sections (business, UX, growth, behavior, etc.)
       ↓
Synthesis Agent connects findings to Knowledge Brain frameworks
       ↓
Pattern Detection finds recurring themes across apps
       ↓
Output: Complete analysis + Framework connections + Patterns detected
```

---

## Quick Start (5 Minutes)

### 1. Start a New App Analysis

```bash
# Input
App: "Flo Health"
Category: "Health & Fitness"

# Creates folder
app_analyses/flo-health/
```

### 2. Research 6 Sections

Use templates in `app_analyses/_SECTION_TEMPLATES/`:

1. **Business Origin** - Founding, business model, competition
2. **User Behavior** - Usage patterns, habits, motivations
3. **Growth Loops (Inception)** - How they grew 2015-2020
4. **UX Analysis** - Interface, flows, design patterns
5. **Growth Loops (Post-AI)** - Modern growth 2020-2025
6. **Voice of Customer** - Reviews, sentiment, community

### 3. Run Synthesis Agent

Synthesis agent:
- Extracts concepts from your 6 sections
- Searches Knowledge Brain (vector search on 200+ frameworks)
- Creates connections in Supabase
- Detects patterns across apps
- Generates `synthesis.md`

### 4. Review Connections

Check `synthesis.md` to see:
- Which frameworks explain this app
- Which concepts emerged
- Which patterns detected
- How it connects to other apps

---

## The 6 Analysis Sections

| Section | Focus | Key Question |
|---------|-------|--------------|
| **1. Business Origin** | Founding, business model | How did they start? How do they make money? |
| **2. User Behavior** | Usage patterns, habits | What do users actually do? Why do they keep using it? |
| **3. Growth Loops (Inception)** | Early growth (2015-2020) | How did they acquire first 10K, 100K, 1M users? |
| **4. UX Analysis** | Interface, flows, design | What makes it easy/hard to use? |
| **5. Growth Loops (Post-AI)** | Modern growth (2020+) | How has growth changed with AI/new tech? |
| **6. Voice of Customer** | Reviews, sentiment | What do users love/hate? |

---

## The Bi-Directional Learning System

### Forward: Frameworks → Apps

Your 200+ frameworks help analyze apps:
- "Let's apply Fogg Behavior Model to Flo's streak feature"
- "Does Loss Aversion explain their retention?"

### Backward: Apps → Frameworks

App insights enrich the Knowledge Brain:
- "Flo uses Fogg Behavior Model → add to framework applications"
- "3 apps use streaks → pattern detected → create pattern doc"

### Over Time: Pattern Library Grows

```
After 1 app:    0 patterns detected
After 3 apps:   1 pattern validated (Streak Mechanics)
After 10 apps:  5 patterns detected
After 50 apps:  23 patterns proven
```

---

## Folder Structure

```
app_analysis_system/
├── CLAUDE.md                      # ⭐ Complete architecture (read this!)
├── README.md                      # This file
│
├── app_analyses/
│   ├── _SECTION_TEMPLATES/       # Templates for each section
│   └── [app-name]/               # Each app gets folder
│       ├── 01-business-origin.md
│       ├── 02-user-behavior.md
│       ├── 03-growth-loops-inception.md
│       ├── 04-ux-analysis.md
│       ├── 05-growth-loops-post-ai.md
│       ├── 06-voice-of-customer.md
│       ├── synthesis.md          # ⭐ Framework connections
│       └── screenshots/
│
├── agents/                        # Agent instructions
│   ├── synthesis_agent.md        # ⭐ Most important agent
│   └── ...
│
├── supabase/                      # Database
│   └── schema.sql                # Complete schema
│
└── outputs/                       # Published outputs
    ├── replit/                   # Case study sites
    └── mobbin_library/           # Interactive gallery
```

---

## Supabase Database

### Tables Created

1. **frameworks** (200+ from Knowledge Brain)
2. **concepts** (sub-components of frameworks)
3. **disciplines** (your 6 core disciplines)
4. **app_analyses** (metadata for each app)
5. **app_framework_connections** (which apps use which frameworks)
6. **patterns** (recurring patterns detected)
7. **observations** (from Knowledge Brain)
8. **app_concepts** (concepts extracted from apps)
9. **synthesis_runs** (track synthesis agent executions)

### Key Queries

**"Which apps use Fogg Behavior Model?"**
```sql
SELECT a.app_name FROM app_analyses a
WHERE 'fogg-model-uuid' = ANY(a.framework_ids);
```

**"What patterns have emerged?"**
```sql
SELECT name, occurrences FROM patterns
WHERE confidence > 0.70
ORDER BY occurrences DESC;
```

---

## The 9 Agents

1. **App Research Orchestrator** - Manages entire analysis
2-7. **Section Agents (6)** - Research each section in parallel
8. **Synthesis Agent** ⭐ - Connects to Knowledge Brain
9. **Pattern Detection Agent** - Finds recurring patterns

---

## Example: Flo Health Analysis

### Input
```
App: Flo Health
Category: Health & Fitness
```

### Output After Synthesis

**Frameworks Detected (11):**
- Fogg Behavior Model (0.95 relevance)
- Loss Aversion (0.90 relevance)
- Network Effects (0.92 relevance)
- Variable Rewards (0.88 relevance)
- ... 7 more

**Concepts Extracted (12):**
- Habit formation via streak mechanics
- Predictive analytics (AI forecasts)
- Community building (forums)
- Freemium conversion model
- ... 8 more

**Patterns Detected (1):**
- "Streak Mechanics for Habit Formation" (also in Duolingo, MyFitnessPal)

**Supabase Updated:**
- 11 app-framework connections created
- 11 frameworks updated with "Applied in: Flo Health"
- 1 pattern occurrence incremented

---

## Publishing Outputs

### Output 1: Replit Site

Beautiful case study websites:
- Individual page per app
- Clean, readable design
- Framework links with tooltips
- Screenshots gallery
- Related apps section

### Output 2: Mobbin-Style Library

Interactive gallery:
- Visual cards with thumbnails
- Filter by category, pattern, framework
- Search by name
- Sort by various criteria
- Quick stats

---

## Implementation Roadmap

### Phase 1: Setup (Week 1)
- ✅ Create folder structure
- ✅ Write CLAUDE.md documentation
- ⏳ Create Supabase database
- ⏳ Migrate 200 frameworks from Airtable
- ⏳ Generate embeddings

### Phase 2: First App (Week 2)
- ⏳ Analyze Flo Health manually
- ⏳ Test synthesis agent
- ⏳ Verify Supabase connections
- ⏳ Refine templates

### Phase 3: Automate (Weeks 3-4)
- ⏳ Build 6 section agents
- ⏳ Build orchestrator
- ⏳ Test end-to-end workflow

### Phase 4: Scale (Month 2)
- ⏳ Analyze 10 apps
- ⏳ Validate patterns
- ⏳ Build publishing pipelines

---

## Next Steps

1. **Read** `CLAUDE.md` for complete architecture
2. **Set up** Supabase database (run `supabase/schema.sql`)
3. **Migrate** 200 frameworks from Airtable
4. **Start** first app analysis (use templates)
5. **Run** synthesis agent to connect findings

---

## Key Principle

**Apps feed insights back to Knowledge Brain**

The more apps you analyze, the richer your pattern library becomes. After 50 apps, you'll be able to:
- Predict what growth tactics work for new apps
- Identify anti-patterns
- Answer "Where else can this pattern apply?"
- Build pattern playbooks by category

---

**Questions?** See `CLAUDE.md` for complete system details, agent workflows, and database schema.
