# APP ANALYSIS SYSTEM - Complete Architecture

**Last Updated**: 2026-01-26
**Version**: v1 (Focused MVP)
**Purpose**: Deep app case study system with bi-directional knowledge brain connection
**Foundation**: Connects to Knowledge Brain (200+ frameworks in Supabase)

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [V1 SCOPE - What We're Building](#v1-scope---what-were-building)
3. [The Bi-Directional Learning System](#the-bi-directional-learning-system)
4. [Folder Structure](#folder-structure)
5. [Supabase Schema (v1 Simplified)](#supabase-schema-v1-simplified)
6. [The 4 Agents (v1)](#the-4-agents-v1)
7. [The Synthesis Agent (Critical)](#the-synthesis-agent-critical)
8. [Complete Example: Flo Health](#complete-example-flo-health)
9. [V1 Success Criteria](#v1-success-criteria)
10. [Implementation Roadmap (5 Weeks)](#implementation-roadmap-5-weeks)
11. [Prompts & Workflows](#prompts--workflows)
12. [Future: v2 & v3](#future-v2--v3)

---

## SYSTEM OVERVIEW

### What This System Does

A **deep app analysis engine** that:

1. **Researches apps** through 6 structured sections (business, UX, growth, etc.)
2. **Generates insights** from deep research in markdown files
3. **Connects findings** back to Knowledge Brain frameworks automatically
4. **Detects patterns** across multiple app analyses
5. **Publishes outputs** to Replit sites and Mobbin-style galleries
6. **Enriches Knowledge Brain** with real-world applications over time

### The 6 Analysis Sections

Every app is analyzed through:

1. **Business Origin** - Founding story, business model evolution, competitive landscape
2. **User Behavior** - Core actions, usage patterns, habit formation
3. **Growth Loops (Inception)** - How they grew initially (2015-2020)
4. **UX Analysis** - Interface design, user flows, key features
5. **Growth Loops (Post-AI)** - How growth changed with AI/modern tech
6. **Voice of Customer** - User reviews, testimonials, community sentiment

### The Big Innovation: Bi-Directional Learning

```
┌─────────────────────────────────────────────────────────────┐
│                KNOWLEDGE BRAIN (200+ Frameworks)            │
│  Frameworks → Concepts → Disciplines                        │
│  Stored in Supabase with vector embeddings                  │
└─────────────────────────────────────────────────────────────┘
                    ↕ (Bi-directional)
              Frameworks inform analyses
              Analyses enrich frameworks
┌─────────────────────────────────────────────────────────────┐
│              APP ANALYSIS SYSTEM (This System)              │
│  Research 6 sections → Synthesis Agent connects            │
│  findings to frameworks → Patterns emerge                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    OVER TIME
┌─────────────────────────────────────────────────────────────┐
│                 PATTERN LIBRARY GROWS                       │
│  "Streak mechanics appear in 8 apps"                        │
│  "Network effects in 15 social apps"                        │
│  "Freemium works for habit-forming apps"                    │
└─────────────────────────────────────────────────────────────┘
```

---

## V1 SCOPE - What We're Building

### Philosophy: Prove the Concept First

v1 is about **validating the core workflow** with 1 complete app analysis before scaling. We're optimizing for:
- ✅ **Learning**: Understand what works before automating everything
- ✅ **Quality**: Manual research ensures deep, accurate insights
- ✅ **Foundation**: Set up schemas and agents that v2 can build on
- ❌ **Not speed**: v1 is intentionally slow to get it right

### What v1 INCLUDES

#### 1. Manual Research (You + Research Agent)
- You do the deep research (2-3 days per app)
- Research Agent structures your findings into Supabase schema
- Covers all 6 sections: Business Origin, User Behavior, Growth Loops (Inception), UX Analysis, Growth Loops (Post-AI), Voice of Customer

#### 2. Structuring Agent
- Converts research findings to structured format
- Saves to Supabase `app_sections` table
- Validates data quality
- Returns confirmation

#### 3. Markdown Agent
- Reads structured data from Supabase
- Creates narrative markdown files for each section
- Adds context and analysis
- Saves locally: `app_analyses/[app-name]/01-business-origin.md`, etc.

#### 4. Synthesis Agent ⭐ (THE CRITICAL ONE)
- Reads all 6 section files (structured data + markdown)
- Queries Knowledge Brain (vector search on 200+ frameworks)
- Extracts concepts (10-20 per app)
- Matches concepts to frameworks (relevance scored)
- Creates connections in Supabase
- Generates `synthesis.md` with framework links
- Updates Knowledge Brain with real-world applications

#### 5. Simplified Supabase Schema
Essential tables only:
- `frameworks` (200+ from Knowledge Brain)
- `app_analyses` (app metadata)
- `app_sections` (structured research data)
- `app_framework_connections` (synthesis results)
- `synthesis_runs` (tracking)

#### 6. One Complete Analysis
- Target app: Flo Health (or similar)
- All 6 sections researched
- Structured data + markdown generated
- 10-15 framework connections identified
- Knowledge Brain enriched

### What v1 EXCLUDES (Coming in v2/v3)

#### Publishing Pipelines (v2)
- ❌ Replit site generation
- ❌ Mobbin-style interactive gallery
- ❌ HTML/CSS templates
- **Why defer**: Need multiple apps first to make gallery worth building

#### Pattern Detection (v2)
- ❌ Pattern Detection Agent
- ❌ `patterns` table in Supabase
- ❌ Cross-app pattern analysis
- **Why defer**: Need 3+ apps minimum to detect patterns

#### Automated Research (v2)
- ❌ 6 separate section agents researching in parallel
- ❌ Web scraping automation
- ❌ API integrations for reviews/sentiment
- **Why defer**: Manual research in v1 ensures quality; automate once workflow is validated

#### Advanced Features (v3)
- ❌ App Research Orchestrator (project manager agent)
- ❌ Parallel processing
- ❌ Background job queues
- ❌ Real-time updates
- **Why defer**: Premature optimization; v1 is sequential and that's fine

### v1 Workflow (Realistic)

```
DAY 1-3: You Research App Manually
├── Business Origin (founding, business model, competition)
├── User Behavior (usage patterns, habit formation)
├── Growth Loops Inception (early growth 2015-2020)
├── UX Analysis (interface, flows, patterns)
├── Growth Loops Post-AI (modern growth 2020+)
└── Voice of Customer (reviews, sentiment)
       ↓
DAY 4: Research Agent Structures Findings
├── Converts notes to structured format
└── Saves to Supabase (app_sections table)
       ↓
DAY 4: Markdown Agent Creates Narratives
├── Reads structured data
└── Generates 6 markdown files
       ↓
DAY 5: Synthesis Agent Connects to Knowledge Brain
├── Extracts 10-20 concepts
├── Vector searches 200+ frameworks
├── Creates connections in Supabase
├── Generates synthesis.md
└── Updates Knowledge Brain
       ↓
OUTPUT:
✅ Structured data in Supabase
✅ 6 section markdown files
✅ synthesis.md with framework connections
✅ Knowledge Brain enriched
✅ Validated workflow for v2 scaling
```

### Why This Scope?

**v1 Goal**: Prove that connecting app analyses to Knowledge Brain creates valuable insights

If v1 succeeds, we'll have:
1. ✅ One complete, high-quality app analysis
2. ✅ Validated that framework connections are accurate and useful
3. ✅ Working Supabase schema and agent prompts
4. ✅ Clear understanding of what to automate in v2
5. ✅ Evidence that the bi-directional learning system works

Then v2 can confidently:
- Automate research (6 section agents)
- Scale to 10+ apps
- Detect patterns
- Build publishing pipelines

**Bottom line**: v1 is slow, manual, and focused. That's intentional. We're learning, not scaling (yet).

---

## THE BI-DIRECTIONAL LEARNING SYSTEM

### How It Works

#### Forward Direction: Frameworks → Apps

**When analyzing an app:**

1. Query Knowledge Brain for relevant frameworks
2. Apply frameworks to understand app behavior
3. Use frameworks as lenses for analysis

**Example:**
- Analyzing Flo Health's streak feature
- Query: "frameworks related to habit formation"
- Result: Fogg Behavior Model, Variable Rewards, Loss Aversion
- Apply these frameworks in User Behavior section

#### Backward Direction: Apps → Frameworks

**After analyzing an app:**

1. Synthesis Agent extracts concepts from analysis
2. Matches concepts to existing frameworks (vector search)
3. Creates connections in Supabase
4. Updates framework records with application examples
5. Detects patterns when concepts appear across multiple apps

**Example:**
- Flo Health analysis reveals "streak mechanics"
- Synthesis Agent matches to "Fogg Behavior Model" framework
- Supabase updated: Fogg Behavior Model now linked to Flo Health
- After 5 apps: Pattern detected "Streak Mechanics for Habit Formation"
- New pattern doc created in Knowledge Brain

### The Compounding Effect

```
App 1 (Flo Health)
  ↓
  Connects to 8 frameworks
  No patterns detected yet

App 2 (Duolingo)
  ↓
  Connects to 10 frameworks
  5 overlap with Flo Health
  Pattern emerging: "Streak mechanics"

App 3 (MyFitnessPal)
  ↓
  Connects to 12 frameworks
  7 overlap with previous apps
  Pattern confirmed: "Streak Mechanics for Habit Formation"
  Pattern doc created in Knowledge Brain

Apps 4-10
  ↓
  More patterns emerge:
  - "Freemium Health Apps"
  - "Community as Retention"
  - "AI Predictions as Value Prop"

Apps 11-50
  ↓
  Pattern library rich enough to:
  - Predict what will work for new apps
  - Identify anti-patterns
  - Generate business insights
  - Answer: "Where else can this pattern apply?"
```

---

## FOLDER STRUCTURE

```
app_analysis_system/
│
├── CLAUDE.md                          # This file - complete system
├── README.md                          # Quick start guide
│
├── app_analyses/                      # All app research lives here
│   ├── _APP_TEMPLATE.md              # Template for complete app analysis
│   ├── _SECTION_TEMPLATES/           # Templates for each section
│   │   ├── 01-business-origin.md
│   │   ├── 02-user-behavior.md
│   │   ├── 03-growth-loops-inception.md
│   │   ├── 04-ux-analysis.md
│   │   ├── 05-growth-loops-post-ai.md
│   │   └── 06-voice-of-customer.md
│   │
│   └── [app-name]/                    # Each app gets a folder
│       ├── 01-business-origin.md      # Section 1 research
│       ├── 02-user-behavior.md        # Section 2 research
│       ├── 03-growth-loops-inception.md
│       ├── 04-ux-analysis.md
│       ├── 05-growth-loops-post-ai.md
│       ├── 06-voice-of-customer.md
│       ├── synthesis.md               # KEY: Connections to Knowledge Brain
│       ├── screenshots/               # Visual assets
│       │   ├── onboarding-01.png
│       │   ├── main-screen.png
│       │   └── feature-x.png
│       └── data/                      # Any metrics/data
│           └── user-stats.json
│
├── agents/                            # Agent configurations
│   ├── app_research_orchestrator.md  # Manages entire research process
│   ├── synthesis_agent.md            # KEY: Connects to Knowledge Brain
│   ├── pattern_detection_agent.md    # Detects recurring patterns
│   ├── section_agents/               # One agent per section
│   │   ├── business_origin_agent.md
│   │   ├── user_behavior_agent.md
│   │   ├── growth_loops_inception_agent.md
│   │   ├── ux_analysis_agent.md
│   │   ├── growth_loops_postai_agent.md
│   │   └── voice_customer_agent.md
│   └── publishing_agents/            # Output generation
│       ├── replit_publisher.md
│       └── mobbin_generator.md
│
├── supabase/                          # Database
│   ├── schema.sql                    # Complete database schema
│   ├── migrations/                   # Schema migrations
│   └── functions/                    # Database functions
│       ├── vector_search.sql
│       └── pattern_detection.sql
│
└── outputs/                           # Generated outputs
    ├── replit/                       # Replit site files
    │   ├── index.html               # Gallery homepage
    │   ├── [app-name].html          # Individual case studies
    │   ├── assets/
    │   │   ├── css/
    │   │   ├── js/
    │   │   └── images/
    │   └── data/
    │       └── apps.json            # App metadata
    │
    └── mobbin_library/              # Mobbin-style interactive gallery
        ├── index.html               # Main gallery
        ├── data.json                # App data
        ├── assets/
        └── filters.js               # Search/filter logic
```

---

## SUPABASE SCHEMA (v1 Simplified)

### Why Supabase Instead of Airtable?

**Key advantages:**
- **Vector embeddings** (pgvector) for semantic search - critical for Synthesis Agent
- **SQL flexibility** for complex queries
- **API-first** for agent integration
- **Scalability** as you add more apps in v2/v3

### Migration from Airtable (Week 1 Task)

```
Current: 200 frameworks in Airtable
       ↓
Step 1: Export Airtable to CSV
Step 2: Generate embeddings (OpenAI text-embedding-3-large)
Step 3: Create Supabase tables
Step 4: Import frameworks with embeddings
       ↓
Result: All frameworks queryable via vector search
```

### v1 Database Tables (5 Essential Tables)

In v1, we're keeping it minimal. Only what's needed for the core workflow.

#### 1. **frameworks** (Core - Your 200 frameworks)

```sql
CREATE TABLE frameworks (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,

  -- Content
  discipline TEXT[], -- ['Evolutionary Psychology', 'Economics']
  principle TEXT, -- Core idea in 1-2 sentences
  mechanics TEXT, -- How it works
  first_seen TEXT, -- Where/when originated
  applications TEXT, -- Real-world examples
  source TEXT, -- Book/paper citation

  -- Relationships
  related_framework_ids UUID[], -- Links to other frameworks
  concept_ids UUID[], -- Links to concepts

  -- Search
  tags TEXT[],
  embedding VECTOR(1536), -- OpenAI embeddings for semantic search

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Application tracking
  app_count INT DEFAULT 0, -- How many apps use this
  last_applied DATE -- Most recent app that used this
);

-- Indexes
CREATE INDEX frameworks_embedding_idx ON frameworks
USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX frameworks_discipline_idx ON frameworks
USING GIN (discipline);

CREATE INDEX frameworks_tags_idx ON frameworks
USING GIN (tags);
```

---

#### 2. **app_analyses** (Metadata for each app)

```sql
CREATE TABLE app_analyses (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  app_name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE, -- URL-friendly (e.g., 'flo-health')

  -- Classification
  category TEXT, -- 'Health & Fitness', 'Social', 'Productivity', etc.

  -- Progress tracking
  status TEXT DEFAULT 'draft', -- draft, researching, structuring, synthesizing, complete
  sections_completed INT DEFAULT 0,
  total_sections INT DEFAULT 6,

  -- File paths
  folder_path TEXT, -- 'app_analyses/flo-health/'

  -- Timestamps
  date_started DATE,
  date_completed DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Analysis results (filled after synthesis)
  key_insights TEXT[], -- 3-5 main takeaways
  framework_count INT DEFAULT 0

  -- v1 Note: Removed publishing fields, pattern fields (coming in v2)
);

-- Indexes
CREATE INDEX app_analyses_status_idx ON app_analyses(status);
```

---

#### 3. **app_sections** (Structured research data - NEW for v1)

This table stores your structured research findings for each of the 6 sections.

```sql
CREATE TABLE app_sections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Relationships
  app_id UUID REFERENCES app_analyses(id) ON DELETE CASCADE,

  -- Section info
  section_type TEXT NOT NULL, -- 'business_origin', 'user_behavior', etc.
  section_number INT NOT NULL, -- 1-6

  -- Structured data (JSONB for flexibility)
  data JSONB NOT NULL,

  -- Markdown path
  markdown_file TEXT, -- Path to generated markdown

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Unique constraint
  UNIQUE(app_id, section_type)
);

-- Indexes
CREATE INDEX app_sections_app_idx ON app_sections(app_id);
CREATE INDEX app_sections_type_idx ON app_sections(section_type);
```

**Why JSONB?** Each section has different fields (founders, users, features, etc.). JSONB gives us flexibility without creating 6 separate tables.

**Example Data** (Business Origin):
```json
{
  "founders": ["Dmitry Gurski", "Yuri Gurski"],
  "founded_year": 2015,
  "founded_location": "Belarus",
  "problem_solved": "Women's health tracking gap",
  "business_model": "Freemium",
  "conversion_rate": "10%",
  "current_users": "50M"
}
```

---

#### 4. **app_framework_connections** (Many-to-many: Apps ↔ Frameworks)

```sql
CREATE TABLE app_framework_connections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Relationships
  app_id UUID REFERENCES app_analyses(id) ON DELETE CASCADE,
  framework_id UUID REFERENCES frameworks(id) ON DELETE CASCADE,

  -- Context
  section TEXT, -- Which section applied this (e.g., 'User Behavior')
  relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
  quote TEXT, -- Specific quote from analysis demonstrating framework

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  detected_by TEXT DEFAULT 'synthesis_agent', -- Which agent made connection

  -- Unique constraint
  UNIQUE(app_id, framework_id, section)
);

-- Indexes
CREATE INDEX app_framework_app_idx ON app_framework_connections(app_id);
CREATE INDEX app_framework_framework_idx ON app_framework_connections(framework_id);
CREATE INDEX app_framework_relevance_idx ON app_framework_connections(relevance_score DESC);
```

---

#### 5. **synthesis_runs** (Track synthesis agent executions)

```sql
CREATE TABLE synthesis_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- What was synthesized
  app_id UUID REFERENCES app_analyses(id) ON DELETE CASCADE,

  -- Results
  concepts_extracted INT,
  frameworks_matched INT,
  patterns_detected INT,
  new_patterns_created INT,

  -- Performance
  duration_seconds INT,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,

  -- Metadata
  agent_version TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX synthesis_runs_app_idx ON synthesis_runs(app_id);
```

---

### Tables DEFERRED to v2

These tables aren't needed for v1 (1 app analysis). We'll add them in v2 when we have 3+ apps and can detect patterns.

**v2 Tables:**
- `concepts` - Sub-components of frameworks (can extract later)
- `disciplines` - Your 6 core disciplines (can add when needed)
- `patterns` - Detected recurring patterns (need 3+ apps)
- `observations` - From Knowledge Brain (future integration)
- `app_concepts` - Detailed concept extraction (v2 enhancement)

**Why defer?** In v1, we're proving the core workflow works. These tables add complexity without immediate value for 1 app.

---

### v1 Key Queries You'll Run

**1. Find frameworks for a concept:**
```sql
-- Semantic search for "habit formation"
SELECT
  f.name,
  f.principle,
  1 - (f.embedding <=> query_embedding) AS similarity
FROM frameworks f
ORDER BY f.embedding <=> query_embedding
LIMIT 10;
```

**2. Show all apps using a framework:**
```sql
-- Which apps use "Fogg Behavior Model"?
SELECT
  a.app_name,
  afc.section,
  afc.relevance_score,
  afc.quote
FROM app_framework_connections afc
JOIN app_analyses a ON afc.app_id = a.id
WHERE afc.framework_id = 'fogg-behavior-model-uuid'
ORDER BY afc.relevance_score DESC;
```

**3. Detect patterns:**
```sql
-- Find framework clusters (frameworks used together often)
SELECT
  f1.name AS framework_1,
  f2.name AS framework_2,
  COUNT(*) AS co_occurrence_count
FROM app_framework_connections afc1
JOIN app_framework_connections afc2
  ON afc1.app_id = afc2.app_id
  AND afc1.framework_id < afc2.framework_id
JOIN frameworks f1 ON afc1.framework_id = f1.id
JOIN frameworks f2 ON afc2.framework_id = f2.id
GROUP BY f1.name, f2.name
HAVING COUNT(*) >= 3
ORDER BY co_occurrence_count DESC;
```

**4. Most-used frameworks:**
```sql
-- Top 20 frameworks by application count
SELECT
  f.name,
  f.discipline,
  COUNT(afc.id) AS app_count
FROM frameworks f
LEFT JOIN app_framework_connections afc ON f.id = afc.framework_id
GROUP BY f.id, f.name, f.discipline
ORDER BY app_count DESC
LIMIT 20;
```

---

## THE 4 AGENTS (v1)

### v1 Agent Architecture (Simplified)

In v1, we have **4 sequential agents** instead of 9. This is intentional to keep scope manageable.

```
┌─────────────────────────────────────────────┐
│   YOU: Manual Research (Days 1-3)          │
│   - Research all 6 sections                 │
│   - Take notes, gather findings             │
│   - Organize information                    │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  AGENT 1: RESEARCH AGENT                    │
│  - Takes your research notes                │
│  - Structures findings per section          │
│  - Validates completeness                   │
│  - Prepares for database                    │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  AGENT 2: STRUCTURING AGENT                 │
│  - Converts to Supabase schema              │
│  - Saves to app_sections table              │
│  - Validates data quality                   │
│  - Returns confirmation                     │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  AGENT 3: MARKDOWN AGENT                    │
│  - Reads structured data                    │
│  - Creates narrative markdown               │
│  - Adds context/analysis                    │
│  - Saves 6 section files locally            │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  AGENT 4: SYNTHESIS AGENT ⭐ CRITICAL       │
│  - Reads structured data + markdown         │
│  - Extracts concepts (10-20)                │
│  - Vector searches frameworks (200+)        │
│  - Creates connections (relevance scored)   │
│  - Updates Supabase                         │
│  - Generates synthesis.md                   │
│  - Enriches Knowledge Brain                 │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│           OUTPUT (v1)                       │
│  ✅ Structured data in Supabase             │
│  ✅ 6 section markdown files                │
│  ✅ synthesis.md with framework connections │
│  ✅ Knowledge Brain enriched                │
└─────────────────────────────────────────────┘
```

### Agent 1: Research Agent (Structuring Your Notes)

**Role**: Convert your manual research into structured format

**v1 Reality**: You do the deep research. This agent organizes it.

**Inputs**:
- Your research notes (text, bullet points, paragraphs)
- App name
- Section type (which of the 6 sections)

**What It Does**:
1. Reads your unstructured notes
2. Identifies key entities (names, dates, metrics, etc.)
3. Maps to section-specific schema
4. Validates required fields are present
5. Formats for Supabase insert

**Outputs**:
- Structured JSON for each section
- Missing data warnings (if any)
- Ready for Structuring Agent

**Example Input (Business Origin)**:
```
Your notes:
"Flo Health founded 2015 by Dmitry and Yuri Gurski in Belarus.
They saw gap in women's health tracking. Raised Series A in 2018.
Now 50M users. Freemium model, 10% convert to premium..."
```

**Example Output (Structured)**:
```json
{
  "section_type": "business_origin",
  "founders": ["Dmitry Gurski", "Yuri Gurski"],
  "founded_year": 2015,
  "founded_location": "Belarus",
  "problem_solved": "Women's health tracking gap",
  "funding_rounds": [{"round": "Series A", "year": 2018}],
  "current_users": "50M",
  "business_model": "Freemium",
  "conversion_rate": "10%"
}
```

---

### Agent 2: Structuring Agent (Database Writer)

**Role**: Save structured data to Supabase

**Inputs**:
- Structured JSON from Research Agent
- App ID (Supabase)
- Section type

**What It Does**:
1. Validates JSON against schema
2. Checks for required fields
3. Inserts into `app_sections` table
4. Updates `app_analyses` progress counter
5. Returns confirmation

**Outputs**:
- Database record ID
- Confirmation of save
- Any validation errors

**v1 Note**: In v1, this is a simple database writer. In v2, it might do more validation/enrichment.

---

### Agent 3: Markdown Agent (Narrative Writer)

**Role**: Create readable markdown narratives from structured data

**Inputs**:
- Structured data from Supabase (all 6 sections)
- App name

**What It Does**:
1. Reads structured data for each section
2. Converts to narrative prose
3. Adds context, transitions, analysis
4. Formats with markdown headers
5. Saves to local files

**Outputs**:
- 6 markdown files:
  - `01-business-origin.md`
  - `02-user-behavior.md`
  - `03-growth-loops-inception.md`
  - `04-ux-analysis.md`
  - `05-growth-loops-post-ai.md`
  - `06-voice-of-customer.md`

**Example** (Business Origin → Markdown):

**Input** (Structured data):
```json
{
  "founders": ["Dmitry Gurski", "Yuri Gurski"],
  "founded_year": 2015,
  "problem_solved": "Women's health tracking gap"
}
```

**Output** (Markdown):
```markdown
# Business Origin: Flo Health

## Founding Story

Flo Health was founded in 2015 by brothers Dmitry and Yuri Gurski
in Belarus. They identified a significant gap in the market for
women's health tracking applications...

## Problem They Solved

Prior to Flo, women's health tracking was...
```

---

### Agents DEFERRED to v2

#### **Agent 2: Business Origin Agent**

**Researches**: `01-business-origin.md`

**Key Questions**:
- Who founded the company? When? Why?
- What problem were they solving?
- How did business model evolve?
- Who are competitors?
- Funding history (if relevant)

**Output Structure**:
```markdown
# Business Origin: [App Name]

## Founding Story
[When, who, why]

## Problem They Solved
[Market gap]

## Business Model Evolution
[Timeline: 2015 → 2018 → 2023]

## Competitive Landscape
[Main competitors, differentiation]

## Key Milestones
- 2015: Founded
- 2018: Series A
- 2020: Hit 10M users
- 2023: $100M ARR

## Key Insights
[3-5 insights about their business strategy]
```

#### **Agent 3: User Behavior Agent**

**Researches**: `02-user-behavior.md`

**Key Questions**:
- What are core user actions?
- How often do users engage?
- What drives retention?
- Are there habit loops?
- What motivates users?

**Output Structure**:
```markdown
# User Behavior: [App Name]

## Core User Actions
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Usage Patterns
- DAU/MAU ratio
- Session frequency
- Time spent
- Retention curves

## Habit Formation
[Are there habit loops? Triggers? Rewards?]

## User Motivations
[Why do users keep using this?]

## Key Insights
[3-5 behavioral insights]
```

#### **Agent 4: Growth Loops (Inception) Agent**

**Researches**: `03-growth-loops-inception.md`

**Key Questions**:
- How did they acquire first 1000 users?
- How did they grow 2015-2020?
- What were primary growth loops?
- Paid vs organic?
- What worked?

**Output Structure**:
```markdown
# Growth Loops (Inception): [App Name]

## Early Growth (0 → 1000 users)
[How they got started]

## Primary Growth Loops (2015-2020)
### Loop 1: [Name]
- Input: [What goes in]
- Action: [What happens]
- Output: [What comes out that feeds back]

### Loop 2: [Name]
...

## Channels
- Paid: [If any]
- Organic: [Word of mouth, SEO, etc.]
- Viral: [Referrals, sharing, etc.]

## What Worked
[Most effective strategies]

## What Failed
[What they tried that didn't work]

## Key Insights
[3-5 growth insights]
```

#### **Agent 5: UX Analysis Agent**

**Researches**: `04-ux-analysis.md`

**Key Questions**:
- What's the onboarding flow?
- What are key screens?
- How is information architecture organized?
- What UX patterns do they use?
- What makes it intuitive (or not)?

**Output Structure**:
```markdown
# UX Analysis: [App Name]

## Onboarding Flow
[Step by step: Screen 1 → Screen 2 → ...]

## Information Architecture
[How is the app organized? Tabs? Navigation?]

## Key Screens
- Home Screen: [Description]
- [Feature Screen]: [Description]
- [Settings]: [Description]

## UX Patterns Used
- [Pattern 1]: [Where/how used]
- [Pattern 2]: [Where/how used]

## Visual Design
[Design aesthetic, color scheme, typography]

## Usability Strengths
[What they do well]

## Usability Weaknesses
[What could improve]

## Key Insights
[3-5 UX insights]
```

#### **Agent 6: Growth Loops (Post-AI) Agent**

**Researches**: `05-growth-loops-post-ai.md`

**Key Questions**:
- How has growth changed 2020-2025?
- Are they using AI/ML for growth?
- New loops enabled by tech?
- How did they adapt?

**Output Structure**:
```markdown
# Growth Loops (Post-AI Era): [App Name]

## Changes Since 2020
[How growth strategy evolved]

## AI/ML Integration
[Are they using AI? How?]

## New Growth Loops
### Loop 1: [Name]
[Enabled by what technology?]

## Impact of Modern Tech
- Personalization: [How]
- Automation: [How]
- New channels: [TikTok, etc.]

## Comparison to Inception Era
[What's different now vs 2015-2020?]

## Key Insights
[3-5 insights about modern growth]
```

#### **Agent 7: Voice of Customer Agent**

**Researches**: `06-voice-of-customer.md`

**Key Questions**:
- What do users say in reviews?
- What do they love?
- What do they complain about?
- What's community sentiment?

**Data Sources**:
- App Store reviews
- Google Play reviews
- Reddit discussions
- Twitter mentions
- User testimonials

**Output Structure**:
```markdown
# Voice of Customer: [App Name]

## Review Analysis
- App Store rating: [X.X/5]
- Google Play rating: [X.X/5]
- Total reviews: [Number]

## What Users Love
1. [Theme 1]: [Quote examples]
2. [Theme 2]: [Quote examples]
3. [Theme 3]: [Quote examples]

## What Users Complain About
1. [Issue 1]: [Quote examples]
2. [Issue 2]: [Quote examples]
3. [Issue 3]: [Quote examples]

## Common Themes
[Patterns across reviews]

## Community Sentiment
[Reddit, Twitter, forums - what's the vibe?]

## Testimonials
[Positive user stories]

## Key Insights
[3-5 insights from user feedback]
```

---

## THE SYNTHESIS AGENT (CRITICAL)

This is the **most important agent** - it connects app analyses back to the Knowledge Brain.

### Synthesis Agent Workflow (Step-by-Step)

```
INPUT: 6 completed section files
      ↓
STEP 1: Extract Concepts
      ↓
STEP 2: Vector Search Frameworks
      ↓
STEP 3: Match Concepts to Frameworks
      ↓
STEP 4: Identify Disciplines
      ↓
STEP 5: Check for Patterns
      ↓
STEP 6: Update Supabase
      ↓
OUTPUT: synthesis.md + Supabase updated
```

### Step 1: Extract Concepts

**Agent reads all 6 sections and identifies:**

- **Behavioral patterns**: "Users check app daily", "Streak mechanics drive engagement"
- **Business insights**: "Freemium converts at 10%", "Network effects from data"
- **UX patterns**: "Gamification with badges", "Push notifications as triggers"
- **Growth tactics**: "Referral loops", "Content marketing", "App Store optimization"

**Output**: List of 10-20 concepts

**Example (Flo Health)**:
```
CONCEPTS EXTRACTED:
1. Habit formation via streak mechanics
2. Predictive analytics (AI forecasts)
3. Community building (forums)
4. Freemium conversion model
5. Health education content
6. Privacy concerns (sensitive data)
7. Network effects from user data
8. Gamification (badges, achievements)
9. Push notifications as triggers
10. Design-first approach (beautiful UI)
11. Personalization engine
12. Social features (sharing cycles)
```

### Step 2: Vector Search Frameworks

**For each concept, query Supabase:**

```python
# Pseudo-code
for concept in concepts_extracted:
    # Generate embedding for concept
    concept_embedding = openai.embeddings.create(
        input=concept.description,
        model="text-embedding-3-large"
    )

    # Vector search Supabase
    results = supabase.rpc('vector_search_frameworks', {
        'query_embedding': concept_embedding,
        'match_count': 5,
        'match_threshold': 0.7
    })

    # Results: Top 5 most similar frameworks
    for framework in results:
        print(f"{framework.name}: {framework.similarity}")
```

**Example query:**
```
Concept: "Habit formation via streak mechanics"
Description: "Flo uses daily streak tracking to create habit loops.
Users are prompted to log data daily, earn streak badges, and fear
losing their streak (loss aversion)."

Vector Search Results:
1. Fogg Behavior Model - 0.94 similarity
2. Variable Rewards - 0.88 similarity
3. Loss Aversion - 0.86 similarity
4. Implementation Intentions - 0.82 similarity
5. Commitment Device - 0.78 similarity
```

### Step 3: Match Concepts to Frameworks

**Agent assesses each match:**

```markdown
CONCEPT: Habit formation via streak mechanics

FRAMEWORK MATCHES:

1. **Fogg Behavior Model** (Behavioral Psychology)
   - Similarity: 0.94
   - Relevance: HIGH
   - Quote from analysis: "Flo uses trigger (period day) + action
     (log data) + reward (streak badge) to create automatic habit loops"
   - Section: User Behavior
   - Confidence: 0.95

2. **Loss Aversion** (Behavioral Economics)
   - Similarity: 0.86
   - Relevance: HIGH
   - Quote: "Users fear breaking their streak more than they value
     starting a new one - loss aversion drives daily engagement"
   - Section: User Behavior
   - Confidence: 0.90

3. **Variable Rewards** (Psychology)
   - Similarity: 0.88
   - Relevance: MEDIUM
   - Quote: "Unpredictable rewards (cycle predictions, new insights)
     keep users checking back"
   - Section: User Behavior
   - Confidence: 0.75
```

### Step 4: Identify Disciplines

**Group frameworks by discipline:**

```markdown
DISCIPLINES INVOLVED:

Evolutionary Psychology (2 frameworks):
- Loss Aversion
- Social Proof

Behavioral Psychology (3 frameworks):
- Fogg Behavior Model
- Variable Rewards
- Implementation Intentions

Economics (2 frameworks):
- Network Effects
- Freemium Pricing

Social Science (1 framework):
- Community Building

Design (2 frameworks):
- Visual Hierarchy
- Onboarding Best Practices
```

### Step 5: Check for Patterns

**Compare to past analyses:**

```python
# Pseudo-code
current_app_frameworks = [list of framework IDs]

# Query: Which other apps used similar framework clusters?
similar_apps = supabase.query("""
    SELECT
        a.app_name,
        COUNT(*) as shared_frameworks,
        array_agg(f.name) as frameworks
    FROM app_framework_connections afc1
    JOIN app_framework_connections afc2
        ON afc1.framework_id = afc2.framework_id
        AND afc1.app_id != afc2.app_id
    JOIN app_analyses a ON afc2.app_id = a.id
    JOIN frameworks f ON afc1.framework_id = f.id
    WHERE afc1.app_id = current_app_id
    GROUP BY a.app_name
    HAVING COUNT(*) >= 3
    ORDER BY shared_frameworks DESC
""")

# If 3+ apps share similar framework cluster → pattern
if len(similar_apps) >= 2:
    pattern_detected = True
    pattern_name = suggest_pattern_name(shared_frameworks)
```

**Example:**
```markdown
PATTERN CHECK:

Checking for similar framework clusters...

MATCH FOUND:
- Current app (Flo Health) uses: Fogg Behavior Model, Loss Aversion, Gamification
- Past apps with same cluster:
  - Duolingo: Fogg Behavior Model, Loss Aversion, Gamification
  - MyFitnessPal: Fogg Behavior Model, Loss Aversion

Shared frameworks: 3
Occurrence count: 3 apps

PATTERN DETECTED: "Streak Mechanics for Habit Formation"
- Status: VALIDATED (3+ occurrences)
- Confidence: 0.85
- Action: Create pattern doc if doesn't exist
```

### Step 6: Update Supabase

**Insert connections:**

```sql
-- 1. Create app_framework_connections
INSERT INTO app_framework_connections (
    app_id,
    framework_id,
    section,
    relevance_score,
    quote
) VALUES
    ('flo-health-uuid', 'fogg-model-uuid', 'User Behavior', 0.95, 'Flo uses trigger...'),
    ('flo-health-uuid', 'loss-aversion-uuid', 'User Behavior', 0.90, 'Users fear breaking...'),
    ('flo-health-uuid', 'network-effects-uuid', 'Growth Loops', 0.92, 'More users → more data...');

-- 2. Update app_analyses
UPDATE app_analyses
SET
    status = 'complete',
    framework_ids = ARRAY['fogg-model-uuid', 'loss-aversion-uuid', ...],
    framework_count = 11,
    date_completed = NOW(),
    key_insights = ARRAY['Habit loops drive retention...', ...],
    patterns_detected = ARRAY['Streak Mechanics for Habit Formation']
WHERE id = 'flo-health-uuid';

-- 3. Update frameworks (add application)
UPDATE frameworks
SET
    app_count = app_count + 1,
    last_applied = NOW()
WHERE id IN (SELECT framework_id FROM app_framework_connections WHERE app_id = 'flo-health-uuid');

-- 4. Create or update pattern
INSERT INTO patterns (name, description, occurrences, app_ids, framework_ids)
VALUES (
    'Streak Mechanics for Habit Formation',
    'Daily streak tracking with loss aversion to drive habit formation',
    3,
    ARRAY['flo-health-uuid', 'duolingo-uuid', 'myfitnesspal-uuid'],
    ARRAY['fogg-model-uuid', 'loss-aversion-uuid', 'gamification-uuid']
)
ON CONFLICT (name) DO UPDATE
SET
    occurrences = patterns.occurrences + 1,
    app_ids = array_append(patterns.app_ids, 'flo-health-uuid'),
    last_updated = NOW();

-- 5. Log synthesis run
INSERT INTO synthesis_runs (
    app_id,
    concepts_extracted,
    frameworks_matched,
    patterns_detected,
    new_patterns_created,
    duration_seconds,
    success
) VALUES (
    'flo-health-uuid',
    12, -- concepts extracted
    11, -- frameworks matched
    1,  -- patterns detected
    0,  -- no new patterns (already existed)
    45, -- seconds
    true
);
```

### Step 7: Generate synthesis.md

**Create markdown file with all connections:**

```markdown
# Synthesis: Flo Health → Knowledge Brain

**Date**: 2026-01-25
**Status**: Complete
**Frameworks Applied**: 11
**Patterns Detected**: 1

---

## CONCEPTS IDENTIFIED

### 1. Habit Formation via Streak Mechanics

**What We Found:**
Flo uses daily streak tracking to create automatic habit loops. Users
are prompted to log data daily, earn streak badges, and fear losing
their streak.

**Frameworks Applied:**

#### Fogg Behavior Model (Behavioral Psychology)
- **Link**: [Supabase UUID: fogg-model-uuid]
- **Relevance**: 0.95 (Very High)
- **Quote**: "Flo uses trigger (period day) + action (log data) +
  reward (streak badge) to create automatic habit loops"
- **Section**: User Behavior
- **Insight**: Fogg's formula (B = MAP) perfectly explains Flo's
  retention. Motivation (track health), Ability (easy logging),
  Prompt (push notifications) → Behavior (daily logging)

#### Loss Aversion (Behavioral Economics)
- **Link**: [Supabase UUID: loss-aversion-uuid]
- **Relevance**: 0.90 (High)
- **Quote**: "Users fear breaking their streak more than they value
  starting a new one"
- **Section**: User Behavior
- **Insight**: Loss aversion is 2x stronger than gain motivation. Flo
  leverages this with "Don't lose your 30-day streak!" messaging

#### Variable Rewards (Psychology)
- **Link**: [Supabase UUID: variable-rewards-uuid]
- **Relevance**: 0.75 (Medium)
- **Quote**: "Unpredictable rewards (cycle predictions, new insights)
  keep users checking back"
- **Section**: User Behavior
- **Insight**: Rewards aren't just streaks - users get unpredictable
  insights ("Did you know...?") which creates excitement

---

### 2. Network Effects from User Data

**What We Found:**
More users → more data → better predictions → attracts more users.
Classic data network effect.

**Frameworks Applied:**

#### Data Network Effects (Economics)
- **Link**: [Supabase UUID: data-network-effects-uuid]
- **Relevance**: 0.96 (Very High)
- **Quote**: "With 50M users, Flo's cycle predictions are more accurate
  than competitors with 5M users"
- **Section**: Growth Loops (Inception)
- **Insight**: This is Flo's moat. Smaller competitors can't catch up
  without similar data scale

#### Network Effects (Economics)
- **Link**: [Supabase UUID: network-effects-uuid]
- **Relevance**: 0.92 (High)
- **Quote**: "The product gets better for all users as more users join"
- **Section**: Business Origin
- **Insight**: Unlike social network effects (more friends = better),
  this is data network effects (more data = better for everyone)

---

[Continue for all 12 concepts...]

---

## DISCIPLINES INVOLVED

### Behavioral Psychology (4 frameworks)
- Fogg Behavior Model
- Variable Rewards
- Implementation Intentions
- Commitment Device

### Evolutionary Psychology (2 frameworks)
- Loss Aversion
- Social Proof

### Economics (3 frameworks)
- Network Effects
- Data Network Effects
- Freemium Pricing

### Social Science (1 framework)
- Community Building

### Design (1 framework)
- Onboarding Best Practices

---

## PATTERNS DETECTED

### Pattern: "Streak Mechanics for Habit Formation"

**Status**: VALIDATED (3+ apps)
**Confidence**: 0.85

**Where Else This Appears:**
- Duolingo (language learning)
- MyFitnessPal (food tracking)

**Common Elements:**
- Daily check-in requirement
- Visible streak counter
- Loss aversion messaging
- Rewards for milestones

**Business Impact:**
- Increases DAU by 40-60%
- Improves retention by 25-35%

**When to Use:**
✅ Daily habit apps
✅ Apps with logging/tracking
✅ Apps where consistency matters

❌ Utility apps
❌ Entertainment apps

**Link to Pattern Doc**: `knowledge_brain/connections/streak-mechanics-habit-formation.md`

---

## CONNECTIONS TO OTHER APPS

### Similar Apps (by framework cluster):
- **Duolingo**: 8 shared frameworks
- **MyFitnessPal**: 6 shared frameworks
- **Calm**: 4 shared frameworks

### Similar Categories:
- Health & Fitness apps with gamification
- Apps using AI for personalization
- Freemium health tracking apps

---

## BUSINESS INSIGHTS

### 1. Habit Loops Drive Retention
**Framework**: Fogg Behavior Model
**Data**: 60% retention at 6 months (vs 20% industry average)
**Why**: Daily streak creates automatic habit

### 2. Network Effects Create Moat
**Framework**: Data Network Effects
**Data**: 50M users = prediction accuracy advantage
**Why**: Competitors can't catch up without similar data

### 3. Freemium Works When Free Version Creates Habit
**Framework**: Freemium Pricing
**Data**: 10% convert to premium after 90 days
**Why**: Free version creates habit, premium offers upgrades

### 4. Community Drives Engagement Beyond Core Loop
**Framework**: Community Building
**Data**: Users in forums have 2x retention
**Why**: Social connections supplement habit loops

### 5. Privacy Concerns Are Real But Manageable
**Framework**: Trust & Transparency
**Data**: 15% churn due to privacy concerns
**Why**: Transparent data practices build trust

---

## NEW FRAMEWORKS SUGGESTED

None at this time. All concepts matched existing frameworks well.

---

## SUPABASE UPDATES COMPLETED

✅ Created 11 app_framework_connections
✅ Updated app_analyses record (status: complete)
✅ Updated 11 frameworks (app_count incremented)
✅ Updated 1 pattern (occurrences incremented)
✅ Logged synthesis_run

---

## NEXT QUESTIONS TO RESEARCH

Based on this analysis, interesting questions for Knowledge Brain:

1. **"Why do streaks work better for some apps than others?"**
   - Flo, Duolingo work; others fail
   - What's the difference?

2. **"How do data network effects compare to social network effects?"**
   - Both are moats, but different mechanisms
   - Which is stronger?

3. **"What makes freemium work for health apps?"**
   - Pattern emerging across Flo, MyFitnessPal, Calm
   - What's the formula?

---

## METADATA

**Frameworks Linked**: 11
**Concepts Extracted**: 12
**Patterns Detected**: 1
**Synthesis Duration**: 45 seconds
**Synthesis Agent Version**: v1.0

**Framework IDs**: [List of UUIDs]
**Pattern IDs**: [streak-mechanics-uuid]

**Supabase Links**:
- App record: [UUID]
- Connections: 11 records
- Frameworks updated: 11 records
- Patterns updated: 1 record
```

---

## COMPLETE EXAMPLE: FLO HEALTH

Let me walk through the entire workflow with a real example.

### Input
```
App: "Flo Health"
Category: "Health & Fitness"
Founded: 2015
```

### Step 1: Orchestrator Creates Structure

```bash
# Folder created
app_analyses/flo-health/
├── screenshots/
└── data/

# Supabase record created
INSERT INTO app_analyses (
    app_name,
    slug,
    category,
    status,
    date_started
) VALUES (
    'Flo Health',
    'flo-health',
    'Health & Fitness',
    'draft',
    '2026-01-25'
);
```

### Step 2: Six Section Agents Run (Parallel)

**Each agent researches and writes markdown:**

`01-business-origin.md` - 2000 words on founding, business model, competition
`02-user-behavior.md` - 2500 words on usage patterns, habit loops
`03-growth-loops-inception.md` - 2000 words on early growth (2015-2020)
`04-ux-analysis.md` - 3000 words on interface, flows, UX patterns
`05-growth-loops-post-ai.md` - 2000 words on modern growth (2020-2025)
`06-voice-of-customer.md` - 1500 words on reviews, sentiment

**Total research**: ~13,000 words across 6 files

### Step 3: Synthesis Agent Runs

**Reads all 6 files (13,000 words) and processes:**

```
[Synthesis Agent Log]

2026-01-25 10:30:15 - Starting synthesis for Flo Health
2026-01-25 10:30:16 - Reading 6 section files...
2026-01-25 10:30:18 - Extracted 12 concepts
2026-01-25 10:30:20 - Generating embeddings for concepts...
2026-01-25 10:30:25 - Querying Supabase for framework matches...
2026-01-25 10:30:35 - Found 47 potential framework matches
2026-01-25 10:30:36 - Filtering by relevance (>0.70)...
2026-01-25 10:30:37 - Selected 11 high-confidence matches
2026-01-25 10:30:38 - Grouping by discipline...
2026-01-25 10:30:39 - Checking for patterns...
2026-01-25 10:30:42 - Pattern detected: "Streak Mechanics" (3 apps)
2026-01-25 10:30:43 - Updating Supabase...
2026-01-25 10:30:50 - Created 11 app_framework_connections
2026-01-25 10:30:51 - Updated app_analyses record
2026-01-25 10:30:52 - Updated 11 framework records
2026-01-25 10:30:53 - Updated 1 pattern record
2026-01-25 10:30:54 - Generating synthesis.md...
2026-01-25 10:31:00 - Synthesis complete!
2026-01-25 10:31:00 - Duration: 45 seconds
```

**Outputs `synthesis.md`** (shown in previous section)

### Step 4: Pattern Detection Agent Runs

```
[Pattern Detection Agent Log]

2026-01-25 10:31:01 - Analyzing framework clusters for Flo Health...
2026-01-25 10:31:05 - Comparing to 9 past analyses...
2026-01-25 10:31:10 - Pattern found: "Streak Mechanics" (Duolingo, MyFitnessPal)
2026-01-25 10:31:12 - Confidence: 0.85 (VALIDATED)
2026-01-25 10:31:13 - Checking if pattern doc exists...
2026-01-25 10:31:14 - Pattern doc exists, updating occurrences...
2026-01-25 10:31:15 - Updated: knowledge_brain/connections/streak-mechanics-habit-formation.md
2026-01-25 10:31:16 - Pattern detection complete!
```

### Final State

**In `app_analyses/flo-health/`:**
- ✅ 01-business-origin.md (2000 words)
- ✅ 02-user-behavior.md (2500 words)
- ✅ 03-growth-loops-inception.md (2000 words)
- ✅ 04-ux-analysis.md (3000 words)
- ✅ 05-growth-loops-post-ai.md (2000 words)
- ✅ 06-voice-of-customer.md (1500 words)
- ✅ synthesis.md (3000 words with framework connections)
- ✅ screenshots/ (10 screenshots)

**In Supabase:**
- ✅ app_analyses record (status: complete)
- ✅ 11 app_framework_connections
- ✅ 11 frameworks updated (app_count incremented)
- ✅ 1 pattern updated (occurrences incremented)
- ✅ 1 synthesis_run logged

**In Knowledge Brain:**
- ✅ Pattern doc updated: `connections/streak-mechanics-habit-formation.md`
- ✅ Frameworks now show "Applied in: Flo Health"

---

## PATTERN LIBRARY GROWTH

### How Patterns Emerge Over Time

**After App 1 (Flo Health):**
```
Frameworks used: 11
Patterns detected: 0 (need 3+ apps for validation)
Pattern candidates: 2 (streak mechanics, freemium health)
```

**After App 2 (Duolingo):**
```
Frameworks used: 10
Overlap with Flo: 5 frameworks
Pattern candidates:
- "Streak Mechanics" (2 apps, confidence: 0.65, status: emerging)
- "Gamification for Learning" (1 app, new)
```

**After App 3 (MyFitnessPal):**
```
Frameworks used: 12
Overlap with Flo: 6 frameworks
Overlap with Duolingo: 5 frameworks

PATTERN VALIDATED: "Streak Mechanics for Habit Formation"
- Apps: Flo, Duolingo, MyFitnessPal
- Frameworks: Fogg Behavior Model, Loss Aversion, Gamification
- Confidence: 0.85
- Status: VALIDATED
→ Create pattern doc in Knowledge Brain
```

**After Apps 4-10:**
```
Total apps analyzed: 10
Total frameworks connections: 98
Total patterns detected: 5

PATTERNS:
1. "Streak Mechanics for Habit Formation" (7 apps)
2. "Freemium Health Apps" (6 apps)
3. "Community as Retention Driver" (5 apps)
4. "AI Predictions as Value Prop" (4 apps)
5. "Onboarding Personalization" (3 apps)
```

**After Apps 11-50:**
```
Total apps analyzed: 50
Total framework connections: 523
Total patterns detected: 23

TOP PATTERNS:
1. "Streak Mechanics" (23 apps) - PROVEN
2. "Freemium Conversion Funnel" (19 apps) - PROVEN
3. "Network Effects from Data" (17 apps) - PROVEN
4. "Community-Driven Retention" (15 apps) - PROVEN
5. "Push Notifications as Triggers" (14 apps) - PROVEN
...

BUSINESS INSIGHTS UNLOCKED:
- Can predict which growth tactics work for new apps
- Can identify anti-patterns (what doesn't work)
- Can answer: "Where else can pattern X apply?"
- Can build pattern playbooks by category
```

### Pattern Doc Example

After detecting "Streak Mechanics" pattern 3+ times, auto-create:

`knowledge_brain/connections/streak-mechanics-habit-formation.md`:

```markdown
# Pattern: Streak Mechanics for Habit Formation

**Status**: VALIDATED
**Confidence**: 0.85
**Occurrences**: 7 apps
**First Detected**: 2026-01-25
**Last Updated**: 2026-02-15

---

## WHAT IS THIS PATTERN?

Daily streak tracking combined with loss aversion to drive habit formation
in apps requiring consistent daily usage.

**Core Mechanism:**
1. User performs action daily (log data, complete lesson, etc.)
2. App tracks consecutive days (streak count)
3. App displays streak prominently
4. User fears losing streak (loss aversion)
5. Fear drives daily return

---

## WHERE IT APPEARS

### Health & Fitness
1. **Flo Health** - Period tracking (50M users)
2. **MyFitnessPal** - Food logging (200M users)
3. **Strava** - Exercise tracking (100M users)
4. **Calm** - Meditation (50M users)

### Learning & Productivity
5. **Duolingo** - Language learning (500M users)
6. **Habitica** - Habit tracking (4M users)
7. **Forest** - Focus timer (10M users)

---

## COMMON ELEMENTS

All 7 apps share:
- ✅ Daily check-in requirement
- ✅ Visible streak counter (usually on home screen)
- ✅ Loss aversion messaging ("Don't break your streak!")
- ✅ Milestone rewards (7, 30, 100, 365 days)
- ✅ Push notifications as reminders
- ✅ Streak freeze/protection (premium feature in some)

---

## FRAMEWORKS THAT EXPLAIN IT

### Primary Frameworks

**1. Fogg Behavior Model** (Behavioral Psychology)
- Appears in: All 7 apps
- How: Trigger (notification) + Ability (easy action) + Motivation (streak) = Behavior

**2. Loss Aversion** (Behavioral Economics)
- Appears in: All 7 apps
- How: Losing streak is 2x more painful than gaining it was pleasurable

**3. Variable Rewards** (Psychology)
- Appears in: 5/7 apps
- How: Milestone badges come at unpredictable intervals, creating excitement

### Supporting Frameworks

**4. Implementation Intentions** (Psychology)
- Appears in: 6/7 apps
- How: "I will log my period every morning" creates automatic behavior

**5. Commitment Device** (Economics)
- Appears in: 4/7 apps
- How: Public commitment to streak (share on social) increases adherence

---

## BUSINESS IMPACT

### Proven Metrics (Aggregated from 7 apps):

**Daily Active Users (DAU):**
- Apps with streaks: 40-60% increase in DAU
- Apps without: Baseline

**Retention:**
- 30-day retention: +25-35%
- 90-day retention: +15-25%
- 365-day retention: +10-15%

**Monetization:**
- "Streak freeze" premium feature: 15-20% of premium subscribers cite this
- Users with 30+ day streaks convert to premium at 2x rate

**Engagement:**
- Average session frequency: 3-5x higher
- Time to habit formation: 18-21 days (vs 66 days average)

---

## WHEN TO USE

### ✅ Works Great For:
- Daily habit apps (fitness, learning, meditation)
- Apps with logging/tracking as core action
- Apps where consistency matters more than intensity
- Apps targeting behavior change
- Apps with clear daily action (log, lesson, workout)

### ❌ Doesn't Work For:
- Utility apps (one-time use like calculators)
- Social apps (organic usage patterns)
- Entertainment apps (binge behavior preferred)
- Professional tools (usage driven by work needs, not habits)
- Shopping apps (purchase frequency too low)

---

## ANTI-PATTERNS (What Fails)

**1. Streak Without Clear Daily Action**
- Example: Photo editing app with streak for "open app daily"
- Why it fails: No meaningful action, feels arbitrary

**2. Too Easy to Game**
- Example: Just opening app counts as day
- Why it fails: Doesn't create real habit, users feel manipulated

**3. Too Punishing**
- Example: No streak freeze, one miss = reset to zero
- Why it fails: Demotivates after first miss, leads to churn

**4. Invisible Streak**
- Example: Streak exists but buried in settings
- Why it fails: No motivational power if not visible

---

## IMPLEMENTATION GUIDE

### Minimum Viable Streak Feature

**Required Elements:**
1. **Visible Counter**: Show streak on home screen
2. **Daily Action**: Clear, easy action that counts
3. **Push Notification**: Remind if haven't done action today
4. **Milestone Rewards**: At least 7, 30, 100-day badges
5. **Loss Aversion Messaging**: "Don't lose your X-day streak!"

**Optional But Recommended:**
6. **Streak Freeze**: Allow 1-2 misses without losing (premium feature)
7. **Streak History**: Show past streaks, not just current
8. **Social Sharing**: Let users share milestone achievements
9. **Streak Leaderboards**: Compare with friends (for competitive apps)

### Design Considerations

**Visual Design:**
- Use fire emoji or similar for streak icon
- Animate streak count when incremented
- Make streak prominent (top of home screen)
- Use red/orange for urgency when at risk

**Copy/Messaging:**
- Frame as loss, not gain: "Don't lose your streak!" not "Keep your streak going!"
- Use countdown: "3 hours left to maintain your streak"
- Celebrate milestones: "🎉 30-day streak! You're in the top 10%"

**Timing:**
- Send reminder notification at user's usual action time
- Send urgency notification 2-3 hours before midnight
- Reset at midnight in user's local timezone

### Common Mistakes to Avoid

1. **Making it too hard** - Daily action should take <5 minutes
2. **Not explaining it** - Onboard users to understand streak value
3. **Forgetting edge cases** - What happens with timezones, travel, etc?
4. **No recovery path** - After breaking streak, give quick win to re-engage
5. **Streak as only retention mechanic** - It works but need other hooks too

---

## VARIATIONS BY CATEGORY

### Health Apps (Flo, MyFitnessPal, Strava, Calm)
- Action: Log health data, track food, record workout, meditate
- Frequency: Daily
- Motivation: Health goals + streak
- Monetization: Premium features enhance streak (predictions, analysis)

### Learning Apps (Duolingo, Habitica)
- Action: Complete lesson, check off habit
- Frequency: Daily
- Motivation: Progress + streak
- Monetization: Streak freeze is premium feature

### Productivity Apps (Forest)
- Action: Use focus timer
- Frequency: Daily (or multiple times)
- Motivation: Visual progress (growing forest) + streak
- Monetization: Different tree types for variety

---

## EVOLUTION OF THE PATTERN

**Phase 1 (2010-2015): Simple Streaks**
- Just a counter
- No loss aversion messaging
- Example: Early Duolingo

**Phase 2 (2015-2020): Enhanced Streaks**
- Added milestone rewards
- Loss aversion copy
- Push notifications
- Example: Modern Duolingo

**Phase 3 (2020-Present): Sophisticated Streaks**
- Streak freeze (premium)
- Streak history/repair
- Social features (compare streaks)
- AI-powered notification timing
- Example: Calm, Flo

**Emerging (2025+): Personalized Streaks**
- AI adjusts difficulty to maintain streak
- Dynamic streak goals (not always daily)
- Mood-based adjustments
- Example: Future iterations

---

## BUSINESS STRATEGY

### For New Apps:

**Week 1:** Implement basic streak (counter + notification)
**Week 2:** Add milestone rewards (7, 30 days)
**Week 3:** Add loss aversion copy
**Week 4:** Measure impact on retention

**Expected Results:**
- 20-30% increase in DAU
- 15-20% increase in 30-day retention

### For Existing Apps:

**If you have:**
- Daily usage already: Add streaks immediately (high impact)
- Weekly usage: Consider weekly streaks instead
- Irregular usage: Streaks probably won't help

---

## RESEARCH QUESTIONS

Based on this pattern, interesting research questions:

1. **Optimal streak reset policy?**
   - Zero-tolerance vs streak freeze vs streak repair
   - Impact on long-term retention

2. **What's the psychological breaking point?**
   - At what streak length does loss aversion max out?
   - Is there a point where anxiety > motivation?

3. **Cultural differences?**
   - Do streaks work equally in all cultures?
   - Hypothesis: More effective in achievement-oriented cultures

4. **Streak length vs habit internalization?**
   - Does habit persist after streak breaks at 90+ days?
   - Can streaks be "graduated" into intrinsic motivation?

---

## RELATED PATTERNS

### Similar Patterns:
- **Progress Bars**: Visual progress without loss aversion
- **Combo Systems**: Gaming-style combos (similar to streaks)
- **Consistency Badges**: Rewards without daily requirement

### Complementary Patterns:
- **Push Notifications**: Triggers for streak maintenance
- **Gamification**: Badges/points enhance streak value
- **Social Proof**: "1M users have 30+ day streaks"

---

## SUPABASE QUERIES

### Apps using this pattern:
```sql
SELECT a.app_name, a.category, afc.relevance_score
FROM app_analyses a
JOIN app_framework_connections afc ON a.id = afc.app_id
WHERE afc.framework_id IN (
    SELECT id FROM frameworks
    WHERE name IN ('Fogg Behavior Model', 'Loss Aversion')
)
GROUP BY a.app_name, a.category
HAVING COUNT(DISTINCT afc.framework_id) >= 2;
```

### Framework co-occurrence:
```sql
-- Which frameworks always appear with "Fogg Behavior Model" in streak pattern?
SELECT f.name, COUNT(*) as co_occurrences
FROM app_framework_connections afc1
JOIN app_framework_connections afc2 ON afc1.app_id = afc2.app_id
JOIN frameworks f ON afc2.framework_id = f.id
WHERE afc1.framework_id = 'fogg-model-uuid'
AND afc1.app_id IN (SELECT unnest(app_ids) FROM patterns WHERE name = 'Streak Mechanics for Habit Formation')
GROUP BY f.name
ORDER BY co_occurrences DESC;
```

---

## METADATA

**Pattern ID**: streak-mechanics-habit-formation
**Status**: VALIDATED
**Confidence**: 0.85
**Occurrences**: 7 apps
**Framework IDs**: [fogg-model-uuid, loss-aversion-uuid, variable-rewards-uuid, ...]
**App IDs**: [flo-health-uuid, duolingo-uuid, myfitnesspal-uuid, ...]
**First Detected**: 2026-01-25
**Last Updated**: 2026-02-15
**Created By**: pattern_detection_agent v1.0
```

---

## PUBLISHING PIPELINES

### Output 1: Replit Site (Case Study Publications)

**Purpose**: Beautiful, readable case studies for each app

**Structure:**
```
replit/
├── index.html              # Gallery of all apps
├── flo-health.html        # Individual case study
├── duolingo.html
├── myfitnesspal.html
└── assets/
    ├── css/style.css
    ├── js/app.js
    └── images/
```

**Generation Process:**
1. Read all 6 section markdown files + synthesis
2. Convert markdown to HTML
3. Apply template (clean, readable design)
4. Generate table of contents
5. Add framework links (hover tooltips)
6. Add screenshots gallery
7. Add "Related Apps" section
8. Deploy to Replit

**Template:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Flo Health Case Study</title>
    <style>
        /* Clean, readable design */
        body { max-width: 800px; margin: 0 auto; font-family: system-ui; }
        h1 { font-size: 2.5em; margin-bottom: 0.2em; }
        .meta { color: #666; margin-bottom: 2em; }
        .section { margin-bottom: 3em; }
        .framework-tag {
            background: #e3f2fd;
            padding: 4px 12px;
            border-radius: 16px;
            cursor: help;
        }
        .framework-tooltip { display: none; }
        .framework-tag:hover .framework-tooltip { display: block; }
    </style>
</head>
<body>
    <nav>
        <a href="index.html">← All Case Studies</a>
    </nav>

    <header>
        <h1>Flo Health</h1>
        <div class="meta">
            Health & Fitness • Founded 2015 • 50M Users
        </div>
        <div class="frameworks">
            <span class="framework-tag">
                Fogg Behavior Model
                <div class="framework-tooltip">
                    Behavior = Motivation × Ability × Prompt
                </div>
            </span>
            <span class="framework-tag">Loss Aversion</span>
            <span class="framework-tag">Network Effects</span>
            <!-- ... 8 more -->
        </div>
    </header>

    <div class="table-of-contents">
        <h2>Contents</h2>
        <ul>
            <li><a href="#business-origin">Business Origin</a></li>
            <li><a href="#user-behavior">User Behavior</a></li>
            <li><a href="#growth-inception">Growth Loops (Inception)</a></li>
            <li><a href="#ux-analysis">UX Analysis</a></li>
            <li><a href="#growth-postai">Growth Loops (Post-AI)</a></li>
            <li><a href="#voice-customer">Voice of Customer</a></li>
            <li><a href="#synthesis">Synthesis & Frameworks</a></li>
        </ul>
    </div>

    <div class="section" id="business-origin">
        <h2>Business Origin</h2>
        <!-- Content from 01-business-origin.md -->
    </div>

    <div class="section" id="user-behavior">
        <h2>User Behavior</h2>
        <!-- Content from 02-user-behavior.md -->
    </div>

    <!-- ... more sections ... -->

    <div class="section" id="synthesis">
        <h2>Synthesis & Frameworks</h2>
        <!-- Content from synthesis.md -->

        <h3>Frameworks Applied</h3>
        <div class="frameworks-detail">
            <div class="framework">
                <h4>Fogg Behavior Model</h4>
                <p><strong>Discipline:</strong> Behavioral Psychology</p>
                <p><strong>How it explains Flo:</strong> ...</p>
                <p><strong>Quote:</strong> "Flo uses trigger (period day) + action (log) + reward (streak)..."</p>
            </div>
            <!-- ... more frameworks ... -->
        </div>
    </div>

    <footer>
        <h3>Related Apps</h3>
        <div class="related-apps">
            <a href="duolingo.html">Duolingo (8 shared frameworks)</a>
            <a href="myfitnesspal.html">MyFitnessPal (6 shared frameworks)</a>
        </div>

        <h3>Patterns Detected</h3>
        <div class="patterns">
            <a href="pattern-streak-mechanics.html">Streak Mechanics for Habit Formation</a>
        </div>
    </footer>
</body>
</html>
```

### Output 2: Mobbin-Style Library (Interactive Gallery)

**Purpose**: Searchable, filterable gallery of all apps analyzed

**Features:**
- Visual cards with screenshots
- Filter by category, pattern, framework
- Sort by date, frameworks used
- Search by name
- Quick stats (frameworks, patterns)

**Structure:**
```
mobbin_library/
├── index.html           # Main gallery
├── data.json            # App metadata
├── style.css
├── app.js               # Filter/search logic
└── assets/
    └── thumbnails/      # App screenshots
```

**data.json:**
```json
{
  "apps": [
    {
      "id": "flo-health",
      "name": "Flo Health",
      "slug": "flo-health",
      "category": "Health & Fitness",
      "thumbnail": "assets/thumbnails/flo-health.png",
      "founded": 2015,
      "users": "50M",
      "frameworks_count": 11,
      "frameworks": [
        {"id": "fogg-model-uuid", "name": "Fogg Behavior Model"},
        {"id": "loss-aversion-uuid", "name": "Loss Aversion"},
        {"id": "network-effects-uuid", "name": "Network Effects"}
        // ... 8 more
      ],
      "patterns": [
        {"id": "streak-mechanics", "name": "Streak Mechanics for Habit Formation"}
      ],
      "key_insights": [
        "Habit loops drive retention",
        "Network effects create moat",
        "Freemium works when free version creates habit"
      ],
      "case_study_url": "flo-health.html"
    },
    {
      "id": "duolingo",
      "name": "Duolingo",
      "category": "Education",
      "thumbnail": "assets/thumbnails/duolingo.png",
      "founded": 2011,
      "users": "500M",
      "frameworks_count": 10,
      "frameworks": [...],
      "patterns": [...]
    }
    // ... more apps
  ],

  "categories": [
    "Health & Fitness",
    "Education",
    "Social",
    "Productivity",
    "Finance"
  ],

  "patterns": [
    {
      "id": "streak-mechanics",
      "name": "Streak Mechanics for Habit Formation",
      "occurrences": 7,
      "apps": ["flo-health", "duolingo", "myfitnesspal", "strava", "calm", "habitica", "forest"]
    }
    // ... more patterns
  ]
}
```

**index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>App Analysis Library</title>
    <style>
        body { font-family: system-ui; padding: 20px; }
        .filters {
            position: sticky;
            top: 0;
            background: white;
            padding: 20px 0;
            border-bottom: 1px solid #ddd;
        }
        .filter-group { margin-bottom: 15px; }
        .app-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .app-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .app-card:hover { transform: translateY(-4px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .app-thumbnail { width: 100%; height: 200px; object-fit: cover; }
        .app-info { padding: 15px; }
        .app-name { font-size: 1.3em; font-weight: 600; margin-bottom: 5px; }
        .app-meta { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        .app-tags { display: flex; flex-wrap: wrap; gap: 5px; }
        .tag {
            background: #f0f0f0;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.85em;
        }
        .tag.pattern { background: #e3f2fd; }
    </style>
</head>
<body>
    <h1>App Analysis Library</h1>
    <p>Deep case studies with framework connections</p>

    <div class="filters">
        <div class="filter-group">
            <label>Search:</label>
            <input type="text" id="search" placeholder="App name..." />
        </div>

        <div class="filter-group">
            <label>Category:</label>
            <select id="category-filter">
                <option value="">All Categories</option>
                <option value="Health & Fitness">Health & Fitness</option>
                <option value="Education">Education</option>
                <option value="Social">Social</option>
                <option value="Productivity">Productivity</option>
            </select>
        </div>

        <div class="filter-group">
            <label>Pattern:</label>
            <select id="pattern-filter">
                <option value="">All Patterns</option>
                <option value="streak-mechanics">Streak Mechanics</option>
                <option value="freemium">Freemium</option>
                <option value="network-effects">Network Effects</option>
            </select>
        </div>

        <div class="filter-group">
            <label>Framework:</label>
            <input type="text" id="framework-search" placeholder="Fogg Behavior Model..." />
        </div>

        <div class="stats">
            <span id="app-count">50 apps</span> analyzed •
            <span id="framework-count">200 frameworks</span> •
            <span id="pattern-count">23 patterns</span> detected
        </div>
    </div>

    <div class="app-grid" id="app-grid">
        <!-- Generated by JS -->
    </div>

    <script src="app.js"></script>
</body>
</html>
```

**app.js:**
```javascript
// Load data
fetch('data.json')
    .then(res => res.json())
    .then(data => {
        window.appData = data;
        renderApps(data.apps);
        setupFilters();
    });

function renderApps(apps) {
    const grid = document.getElementById('app-grid');
    grid.innerHTML = '';

    apps.forEach(app => {
        const card = document.createElement('div');
        card.className = 'app-card';
        card.onclick = () => window.location.href = app.case_study_url;

        card.innerHTML = `
            <img src="${app.thumbnail}" class="app-thumbnail" alt="${app.name}" />
            <div class="app-info">
                <div class="app-name">${app.name}</div>
                <div class="app-meta">
                    ${app.category} • ${app.users} users • ${app.frameworks_count} frameworks
                </div>
                <div class="app-tags">
                    ${app.patterns.map(p => `
                        <span class="tag pattern">${p.name}</span>
                    `).join('')}
                    <span class="tag">${app.frameworks_count} frameworks</span>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

function setupFilters() {
    // Search filter
    document.getElementById('search').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = window.appData.apps.filter(app =>
            app.name.toLowerCase().includes(query)
        );
        renderApps(filtered);
    });

    // Category filter
    document.getElementById('category-filter').addEventListener('change', (e) => {
        const category = e.target.value;
        const filtered = category
            ? window.appData.apps.filter(app => app.category === category)
            : window.appData.apps;
        renderApps(filtered);
    });

    // Pattern filter
    document.getElementById('pattern-filter').addEventListener('change', (e) => {
        const patternId = e.target.value;
        const filtered = patternId
            ? window.appData.apps.filter(app =>
                app.patterns.some(p => p.id === patternId)
              )
            : window.appData.apps;
        renderApps(filtered);
    });

    // Framework search
    document.getElementById('framework-search').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = window.appData.apps.filter(app =>
            app.frameworks.some(f => f.name.toLowerCase().includes(query))
        );
        renderApps(filtered);
    });
}
```

---

## IMPLEMENTATION ROADMAP (5 Weeks)

**Philosophy**: v1 is about proving the concept works with ONE complete app analysis. We're not scaling yet—we're learning.

### Week 1: Foundation Setup

**Goal**: Get Supabase ready + 4 agents built

**Tasks:**

**Day 1-2: Supabase Setup**
- [ ] Create Supabase project
- [ ] Run `schema.sql` to create 5 v1 tables:
  - `frameworks` (200 from Airtable)
  - `app_analyses`
  - `app_sections` (new JSONB table)
  - `app_framework_connections`
  - `synthesis_runs`
- [ ] Export 200 frameworks from Airtable to CSV
- [ ] Generate embeddings (OpenAI `text-embedding-3-large`)
- [ ] Import frameworks with embeddings to Supabase
- [ ] Test vector search query manually

**Day 3: Build Research Agent**
- [ ] Create agent prompt
- [ ] Test: Input your notes → Output structured JSON
- [ ] Validate JSON structure matches app_sections schema

**Day 4: Build Structuring + Markdown Agents**
- [ ] Structuring Agent: JSON → Supabase insert
- [ ] Markdown Agent: Supabase data → narrative .md files
- [ ] Test both agents end-to-end

**Day 5: Build Synthesis Agent (CRITICAL)**
- [ ] Create synthesis agent prompt
- [ ] Test vector search integration
- [ ] Test concept extraction
- [ ] Test framework matching
- [ ] Test Supabase update logic

**Day 6-7: Testing & Refinement**
- [ ] Test all 4 agents sequentially
- [ ] Fix bugs
- [ ] Refine prompts
- [ ] Document workflow

**Deliverable**: ✅ Supabase ready, ✅ 4 agents functional

---

### Week 2-3: Manual Research (Days 8-17)

**Goal**: You manually research Flo Health across all 6 sections

**Day 8-10: Sections 1-3**
- [ ] **Business Origin**: Research founding, business model, competition
  - Founders, timeline, funding, business model evolution
  - Competitors, differentiation
  - Key milestones
- [ ] **User Behavior**: Research usage patterns, habit formation
  - Core actions, frequency, retention
  - Habit loops, motivations
  - Behavioral insights
- [ ] **Growth Loops (Inception)**: Research early growth 2015-2020
  - First 1000 users
  - Primary growth loops
  - Channels (paid, organic, viral)
  - What worked / failed

**Day 11-14: Sections 4-6**
- [ ] **UX Analysis**: Research interface, flows, patterns
  - Onboarding flow (step by step)
  - Information architecture
  - Key screens, UX patterns
  - Visual design, usability
- [ ] **Growth Loops (Post-AI)**: Research modern growth 2020-2025
  - How growth changed
  - AI/ML integration
  - New growth loops
  - Impact of modern tech
- [ ] **Voice of Customer**: Research reviews, sentiment
  - App Store / Google Play reviews
  - Reddit, Twitter, forums
  - What users love / complain about
  - Common themes

**Day 15-17: Organization & Notes**
- [ ] Organize all research notes
- [ ] Gather screenshots (10-15 key screens)
- [ ] Collect data/metrics found
- [ ] Prepare notes for Research Agent

**Deliverable**: ✅ 6 sections researched, ✅ Notes organized

---

### Week 4: Structured Data + Synthesis (Days 18-24)

**Goal**: Convert research to structured data, run synthesis, generate markdown

**Day 18-19: Research Agent → Structured Data**
- [ ] Feed your Business Origin notes to Research Agent
- [ ] Review JSON output, refine
- [ ] Repeat for all 6 sections
- [ ] Fix any structure issues

**Day 20: Structuring Agent → Supabase**
- [ ] Run Structuring Agent on all 6 JSON outputs
- [ ] Verify data saved correctly in `app_sections` table
- [ ] Check `app_analyses` progress counter
- [ ] Validate database records

**Day 21: Markdown Agent → Narrative Files**
- [ ] Run Markdown Agent to generate 6 .md files
- [ ] Review generated narratives
- [ ] Edit for quality (add context, analysis)
- [ ] Ensure markdown formatting correct

**Day 22-23: Synthesis Agent ⭐ (THE BIG ONE)**
- [ ] Run Synthesis Agent on all 6 sections
- [ ] Review concept extraction (should find 10-20)
- [ ] Review framework matches (relevance scores > 0.70)
- [ ] Verify Supabase connections created
- [ ] Check `synthesis.md` output
- [ ] Validate Knowledge Brain enrichment

**Day 24: Quality Check**
- [ ] Review entire Flo Health analysis
- [ ] Check all markdown files for quality
- [ ] Verify Supabase data integrity
- [ ] Test framework connections queries
- [ ] Document learnings

**Deliverable**: ✅ Complete Flo Health analysis, ✅ Supabase updated, ✅ synthesis.md

---

### Week 5: Reflection & v2 Planning (Days 25-30)

**Goal**: Reflect on v1, document learnings, plan v2

**Day 25-26: Retrospective**
- [ ] What worked well?
  - Which agents performed well?
  - Was the manual research effective?
  - Are framework connections accurate?
- [ ] What needs improvement?
  - Which agents need refinement?
  - What data is missing?
  - What's hard to find during research?
- [ ] What surprised you?
  - Unexpected insights?
  - Framework connections you didn't anticipate?

**Day 27-28: Documentation**
- [ ] Update agent prompts based on learnings
- [ ] Refine section templates
- [ ] Document research best practices
- [ ] Create research checklist for v2
- [ ] Update schema if needed

**Day 29: v2 Planning**
- [ ] Decide: Should we automate research? (6 section agents)
- [ ] Decide: Ready to analyze 3+ apps for pattern detection?
- [ ] Decide: What should v2 include?
- [ ] Create v2 roadmap
- [ ] Prioritize v2 features

**Day 30: Validation**
- [ ] Review synthesis.md—does it provide valuable insights?
- [ ] Check framework connections—are they accurate and useful?
- [ ] Ask: "Did connecting to Knowledge Brain work?"
- [ ] Ask: "Is this worth scaling to 10+ apps?"
- [ ] Decision: GO/NO-GO on v2

**Deliverable**: ✅ v1 learnings documented, ✅ v2 plan ready

---

## V1 Success Criteria (What "Success" Looks Like)

By end of Week 5, v1 is successful if:

1. ✅ **Complete Analysis**: Flo Health has all 6 sections + synthesis.md
2. ✅ **Framework Connections**: 10-15 accurate framework matches with quotes
3. ✅ **Supabase Works**: All 5 tables populated correctly
4. ✅ **Synthesis Quality**: synthesis.md provides insights you couldn't get manually
5. ✅ **Agents Work**: All 4 agents run without major bugs
6. ✅ **Learning Captured**: You understand what to automate/improve in v2
7. ✅ **Decision Made**: Clear GO/NO-GO on building v2

**If successful** → Move to v2: Automate research, analyze 3+ apps, detect patterns

**If not successful** → Iterate on v1: Fix agents, refine workflow, try again with different app

---

## What We're NOT Doing in v1

To keep scope manageable, v1 explicitly excludes:

**NOT in v1:**
- ❌ Automated research (you research manually)
- ❌ 6 section agents researching in parallel
- ❌ Pattern detection (need 3+ apps)
- ❌ Publishing pipelines (Replit, Mobbin)
- ❌ Orchestrator agent (sequential workflow is fine)
- ❌ Multiple apps (just Flo Health)
- ❌ Optimization for speed (v1 is intentionally slow)

**Why?** We're learning, not scaling. Prove it works first.

---

## PROMPTS & WORKFLOWS

### Prompt: Start New App Analysis

```
You are the App Research Orchestrator. Your job is to manage the complete
analysis of an app.

APP TO ANALYZE:
Name: [App Name]
Category: [Category]
Founded: [Year] (if known)

INSTRUCTIONS:

1. Create folder structure:
   - app_analyses/[slug]/
   - app_analyses/[slug]/screenshots/
   - app_analyses/[slug]/data/

2. Create Supabase record:
   - Table: app_analyses
   - Fields: app_name, slug, category, status (draft), date_started

3. Trigger 6 section research agents:
   - Business Origin Agent → 01-business-origin.md
   - User Behavior Agent → 02-user-behavior.md
   - Growth Loops Inception Agent → 03-growth-loops-inception.md
   - UX Analysis Agent → 04-ux-analysis.md
   - Growth Loops Post-AI Agent → 05-growth-loops-post-ai.md
   - Voice of Customer Agent → 06-voice-of-customer.md

4. Monitor progress:
   - Update sections_completed counter in Supabase
   - When all 6 complete → trigger Synthesis Agent

5. After synthesis:
   - Trigger Pattern Detection Agent
   - Update status to "complete"

OUTPUT:
- Folder created: [path]
- Supabase record: [UUID]
- 6 section files: [list paths]
- Synthesis: [path to synthesis.md]
- Status: Complete
```

---

### Prompt: Synthesis Agent

```
You are the Synthesis Agent. Your job is to connect app analysis findings
back to the Knowledge Brain.

INPUT FILES:
- app_analyses/[app-name]/01-business-origin.md
- app_analyses/[app-name]/02-user-behavior.md
- app_analyses/[app-name]/03-growth-loops-inception.md
- app_analyses/[app-name]/04-ux-analysis.md
- app_analyses/[app-name]/05-growth-loops-post-ai.md
- app_analyses/[app-name]/06-voice-of-customer.md

SUPABASE CONNECTION:
- Database: [connection string]
- Frameworks table: 200+ frameworks with embeddings

WORKFLOW:

STEP 1: EXTRACT CONCEPTS
Read all 6 files. Identify:
- Behavioral patterns (e.g., "daily streak mechanics")
- Business insights (e.g., "freemium converts at 10%")
- UX patterns (e.g., "gamification with badges")
- Growth tactics (e.g., "referral loops")

Output: List of 10-20 concepts with descriptions

STEP 2: VECTOR SEARCH FRAMEWORKS
For each concept:
1. Generate embedding (OpenAI text-embedding-3-large)
2. Query Supabase:
   SELECT name, principle, discipline,
          1 - (embedding <=> $1) AS similarity
   FROM frameworks
   ORDER BY embedding <=> $1
   LIMIT 5

3. Filter results where similarity > 0.70

Output: Top 5 frameworks per concept

STEP 3: MATCH CONCEPTS TO FRAMEWORKS
For each concept-framework pair:
1. Assess relevance (0-1 score)
2. Find specific quote from analysis
3. Identify which section revealed this
4. Calculate confidence

Keep only matches with:
- Relevance > 0.70
- Clear quote evidence

Output: 10-15 high-confidence framework matches

STEP 4: IDENTIFY DISCIPLINES
Group frameworks by discipline:
- Count frameworks per discipline
- Note which disciplines most relevant

Output: List of disciplines with framework counts

STEP 5: CHECK FOR PATTERNS
Query Supabase for similar apps:
SELECT app_name, COUNT(*) as shared_frameworks
FROM app_framework_connections afc1
JOIN app_framework_connections afc2
  ON afc1.framework_id = afc2.framework_id
WHERE afc1.app_id = $current_app_id
GROUP BY app_name
HAVING COUNT(*) >= 3

If 3+ apps share similar framework cluster:
- Pattern detected!
- Suggest pattern name
- Calculate confidence

Output: Patterns detected (if any)

STEP 6: UPDATE SUPABASE
Execute these SQL statements:

-- Insert framework connections
INSERT INTO app_framework_connections (
    app_id, framework_id, section, relevance_score, quote
) VALUES (...);

-- Update app_analyses
UPDATE app_analyses
SET
    status = 'complete',
    framework_ids = ARRAY[...],
    framework_count = X,
    key_insights = ARRAY[...],
    patterns_detected = ARRAY[...],
    date_completed = NOW()
WHERE id = $app_id;

-- Update frameworks
UPDATE frameworks
SET app_count = app_count + 1, last_applied = NOW()
WHERE id IN (...);

-- Create/update patterns
INSERT INTO patterns (...)
ON CONFLICT (name) DO UPDATE ...;

-- Log synthesis run
INSERT INTO synthesis_runs (...) VALUES (...);

STEP 7: GENERATE synthesis.md
Create markdown file with:
- All concepts identified
- All framework matches with quotes
- Disciplines involved
- Patterns detected
- Business insights
- Supabase metadata

OUTPUT:
- synthesis.md file created
- Supabase updated
- Pattern alerts (if any)
- Summary of connections made
```

---

### Prompt: Pattern Detection Agent

```
You are the Pattern Detection Agent. Your job is to find recurring patterns
across multiple app analyses.

INPUT:
- Current app analysis (just completed)
- All past app analyses (Supabase query)
- Current patterns library

WORKFLOW:

STEP 1: LOAD CURRENT APP FRAMEWORKS
SELECT framework_id, framework_name, section, relevance_score
FROM app_framework_connections afc
JOIN frameworks f ON afc.framework_id = f.id
WHERE afc.app_id = $current_app_id

STEP 2: FIND SIMILAR APPS
Query apps with overlapping frameworks:

SELECT
    a.app_name,
    a.id as app_id,
    COUNT(*) as shared_framework_count,
    array_agg(f.name) as shared_frameworks
FROM app_framework_connections afc1
JOIN app_framework_connections afc2
    ON afc1.framework_id = afc2.framework_id
    AND afc1.app_id != afc2.app_id
JOIN app_analyses a ON afc2.app_id = a.id
JOIN frameworks f ON afc1.framework_id = f.id
WHERE afc1.app_id = $current_app_id
GROUP BY a.app_name, a.id
HAVING COUNT(*) >= 3
ORDER BY shared_framework_count DESC

STEP 3: DETECT PATTERNS
For each framework cluster that appears 3+ times:
1. Check if pattern already exists
2. If exists: Update occurrence count, add current app
3. If new: Create pattern record

Pattern creation threshold:
- Minimum 3 apps
- Minimum 3 shared frameworks
- Framework cluster must be meaningful (not random overlap)

STEP 4: CALCULATE CONFIDENCE
Pattern confidence =
    (occurrences / total_apps_analyzed) *
    (shared_frameworks / avg_frameworks_per_app) *
    (relevance_scores_avg)

Confidence levels:
- 0.30-0.50: Hypothesis (emerging pattern)
- 0.50-0.70: Validated (clear pattern)
- 0.70-1.00: Proven (strong pattern)

STEP 5: SUGGEST NEW FRAMEWORK
If pattern is strong but not in frameworks table:
- Suggest formalizing as new framework
- Propose name, principle, mechanics
- Link to pattern doc

STEP 6: UPDATE KNOWLEDGE BRAIN
If pattern reaches threshold:
- Create pattern doc in knowledge_brain/connections/
- Use pattern template
- Document all occurrences
- Add business applications
- Update Supabase patterns table

OUTPUT:
- Patterns detected: [count]
- Patterns updated: [list]
- New patterns created: [list]
- Framework suggestions: [list]
- Knowledge Brain docs created: [paths]
```

---

**END OF DOCUMENTATION**

---

## NEXT STEPS

1. ✅ Folder structure created
2. ✅ CLAUDE.md written (this document)
3. ⏳ Create section templates
4. ⏳ Create synthesis agent instructions
5. ⏳ Create Supabase schema SQL file
6. ⏳ Migrate frameworks from Airtable
7. ⏳ Start first app analysis (Flo Health)

**This document is your complete system memory. Everything we discussed is here.**
