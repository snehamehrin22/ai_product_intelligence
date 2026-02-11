1# KNOWLEDGE BRAIN - Complete System Architecture

**Last Updated**: 2026-01-25
**Purpose**: Multi-disciplinary thinking system for understanding human behavior through frameworks
**Foundation**: 200+ frameworks in Airtable across 6 disciplines

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [The 3-Layer Architecture](#the-3-layer-architecture)
3. [Agent Architecture (v1 → v2 → v3)](#agent-architecture)
4. [The 8 Agents Defined](#the-8-agents-defined)
5. [Airtable Schema](#airtable-schema)
6. [Workflows & Operating Cadence](#workflows--operating-cadence)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Example: Complete Workflow](#example-complete-workflow)
9. [Prompts & Templates](#prompts--templates)

---

## SYSTEM OVERVIEW

### What This System Does

A **multi-disciplinary knowledge library + research workspace** for understanding human behavior through different lenses:

1. **Stores 200+ frameworks** from books, papers, research (in Airtable)
2. **Analyzes phenomena** by applying frameworks through 6 disciplines
3. **Detects patterns** across multiple analyses
4. **Generates insights** for business/product applications
5. **Compounds knowledge** over time

### Core Disciplines

1. **Evolutionary Psychology** - Why humans behave this way
2. **Anthropology** - How cultures organize
3. **History** - What historical factors matter
4. **Social Science** - How societies function
5. **Economics** - What incentives drive behavior
6. **Geopolitics** - How geography shapes behavior

### Example Questions This Helps Answer

- "Why did matcha become popular in the US?"
- "Why does Vietnam do community well?"
- "Why is the Swift economy so massive?"
- "Why did my dad rush me?" (personal)
- "Why are Owala bottles everywhere?"

---

## THE 3-LAYER ARCHITECTURE

### Layer 1: FRAMEWORKS (Airtable - Source of Truth)

**Your 200+ frameworks organized by discipline**

```
AIRTABLE BASE: Frameworks
├── Evolutionary Psychology (40+ frameworks)
│   ├── Costly Signaling Theory
│   ├── Kin Selection
│   ├── Reciprocal Altruism
│   ├── Group Selection
│   └── ...
├── Anthropology (30+ frameworks)
│   ├── Kinship Systems
│   ├── Ritual & Ceremony
│   ├── Cultural Diffusion
│   └── ...
├── History (30+ frameworks)
├── Social Science (30+ frameworks)
├── Economics (30+ frameworks)
└── Geopolitics (30+ frameworks)
```

**Each framework contains:**
- Name
- Discipline (multi-select)
- Principle (core idea in 1-2 sentences)
- Mechanics (how it works)
- First Seen (original context)
- Applications (real-world examples)
- Related Frameworks (linked records)
- Source (book/paper citation)
- Tags (topical)

### Layer 2: ANALYSES (Markdown + Airtable Metadata)

**Long-form research documents applying frameworks to observations**

**In Markdown** (`analyses/[topic]/synthesis.md`):
- Full multi-lens analysis (6 disciplines)
- Evidence and citations
- Synthesis across disciplines
- Business applications

**In Airtable** (Research table - metadata only):
- Topic name
- Frameworks used (linked records)
- Disciplines applied
- Status
- Key insights (3-5 bullets)
- File path to markdown

### Layer 3: PATTERNS (AI-Detected + Human-Validated)

**Meta-patterns that emerge across multiple analyses**

**In Markdown** (`connections/[pattern-name].md`):
- Pattern description
- Where it appears (multiple analyses)
- Underlying mechanisms
- Business applications

**In Airtable** (Patterns table):
- Pattern name
- Source research (linked records)
- Related frameworks
- Occurrences count
- File path

---

## AGENT ARCHITECTURE

### Evolution: v1 → v2 → v3

```
v1 (Week 1)                v2 (Weeks 2-4)             v3 (Month 2+)
Manual + Basic AI          Semi-Automated              Fully Agentic
├── You select             ├── AI suggests             ├── AI does everything
├── You research           ├── You approve             ├── You validate outputs
├── Claude writes          ├── Agents research         ├── You make decisions
└── You edit               └── Agents draft            └── Continuous learning
```

### The Complete Agent System (v3)

```
┌─────────────────────────────────────────────────────────┐
│                    YOU (Human)                          │
│  - Capture observations                                 │
│  - Review AI outputs                                    │
│  - Validate patterns                                    │
│  - Make decisions                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         1. OBSERVATION CAPTURE AGENT                    │
│  Input: "Why did matcha become popular?"                │
│  - Analyzes question type                               │
│  - Routes to research pipeline                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         2. FRAMEWORK RETRIEVAL AGENT                    │
│  - Queries Airtable (200 frameworks)                    │
│  - Vector search for semantic relevance                 │
│  - Ranks by relevance score                             │
│  - Returns: Top 15 frameworks                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         3. RESEARCH AGENT                               │
│  - Web search (trends, articles, data)                  │
│  - Academic papers                                      │
│  - Your past analyses                                   │
│  - Compiles evidence dossier                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         4. DISCIPLINE AGENTS (6 in Parallel)            │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Evolutionary │  │ Anthropology │  │   History    │ │
│  │    Agent     │  │    Agent     │  │    Agent     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Social    │  │   Economics  │  │ Geopolitics  │ │
│  │    Agent     │  │    Agent     │  │    Agent     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  Each applies frameworks from their discipline          │
│  Each writes their analysis section                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         5. SYNTHESIS AGENT                              │
│  - Combines 6 discipline analyses                       │
│  - Identifies overlapping insights                      │
│  - Resolves contradictions                              │
│  - Writes unified explanation                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         6. PATTERN DETECTION AGENT                      │
│  - Compares to past analyses                            │
│  - Identifies recurring themes                          │
│  - Suggests new frameworks to formalize                 │
│  - Updates pattern library                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         7. EVIDENCE AGENT                               │
│  - Fact-checks all claims                               │
│  - Adds citations                                       │
│  - Links to sources                                     │
│  - Flags unverified claims                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         8. APPLICATION AGENT                            │
│  - Identifies business implications                     │
│  - Suggests product applications                        │
│  - Links to similar examples                            │
│  - Generates actionable insights                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              OUTPUT (Back to You)                       │
│  - Complete multi-lens analysis (markdown)              │
│  - Patterns identified                                  │
│  - Business applications                                │
│  - Airtable updated with metadata                      │
└─────────────────────────────────────────────────────────┘
```

---

## THE 8 AGENTS DEFINED

### 1. Observation Capture Agent

**Purpose**: Intake and classify your observations

**Inputs**:
- Question ("Why did matcha become popular?")
- Phenomenon ("I noticed Owala bottles everywhere")
- Hypothesis ("I think matcha is costly signaling")

**Outputs**:
- Observation type classification
- Initial framework suggestions (based on keywords)
- Routing to appropriate research pipeline

**v1**: Manual capture in notes
**v2**: Voice/text capture with basic classification
**v3**: Automatic classification + framework pre-suggestion

---

### 2. Framework Retrieval Agent

**Purpose**: Find relevant frameworks from your 200+ in Airtable

**Inputs**:
- Observation text
- Observation type
- Context

**Process**:
1. Embed observation text (vector)
2. Search Airtable frameworks (semantic search)
3. Rank by relevance score
4. Filter by discipline diversity (ensure all 6 disciplines represented)
5. Return top 15 frameworks

**Outputs**:
- Top 15 frameworks with relevance scores
- Organized by discipline
- Brief explanation of why each is relevant

**v1**: Manual search in Airtable
**v2**: Vector search with approval step
**v3**: Automatic retrieval with confidence scores

---

### 3. Research Agent

**Purpose**: Gather evidence and context

**Inputs**:
- Observation
- Selected frameworks

**Tasks**:
- **Web Search**: Google trends, articles, news
- **Academic Search**: Papers, studies, research
- **Historical Search**: Timeline, precedents
- **Data Search**: Stats, demographics, pricing
- **Internal Search**: Your past analyses on similar topics

**Outputs**:
- Evidence dossier organized by type
- Citations with links
- Data visualizations (where applicable)
- Related past research

**v1**: Manual web research
**v2**: Automated web search + article summaries
**v3**: Multi-source research with quality scoring

---

### 4. Discipline Agents (6 Specialized Agents)

Each discipline has a specialized agent that applies frameworks from that field.

#### 4.1 Evolutionary Psychology Agent

**Frameworks it uses**:
- Costly Signaling
- Kin Selection
- Reciprocal Altruism
- Group Selection
- Status Games
- Sexual Selection
- Parental Investment

**What it looks for**:
- Status signaling behavior
- Tribal/in-group dynamics
- Reproductive fitness signals
- Survival mechanisms
- Social proof patterns

**Output**: Evolutionary Psychology analysis section

---

#### 4.2 Anthropology Agent

**Frameworks it uses**:
- Kinship Systems
- Ritual & Ceremony
- Cultural Diffusion
- Symbolic Capital
- Rites of Passage
- Cultural Transmission

**What it looks for**:
- Cultural patterns
- Ritual behaviors
- Identity formation
- Community structures
- Cultural meaning

**Output**: Anthropological analysis section

---

#### 4.3 History Agent

**Frameworks it uses**:
- Agricultural Revolution
- Technological Determinism
- Path Dependence
- Historical Precedents
- Cultural Evolution

**What it looks for**:
- Timeline of changes
- Historical parallels
- Technological shifts
- Previous similar phenomena
- Long-term trends

**Output**: Historical analysis section

---

#### 4.4 Social Science Agent

**Frameworks it uses**:
- Social Capital
- Network Effects
- Trust Formation
- Collective Action
- Social Proof
- Conformity

**What it looks for**:
- Social dynamics
- Trust mechanisms
- Network structures
- Group behavior
- Social influence

**Output**: Social science analysis section

---

#### 4.5 Economics Agent

**Frameworks it uses**:
- Veblen Goods
- Network Effects
- Game Theory
- Transaction Costs
- Supply & Demand
- Incentive Structures

**What it looks for**:
- Pricing dynamics
- Market mechanisms
- Incentive alignment
- Economic value
- Resource allocation

**Output**: Economic analysis section

---

#### 4.6 Geopolitics Agent

**Frameworks it uses**:
- Geographic Determinism
- Resource Scarcity
- Trade Routes
- Strategic Position
- Cultural Flows

**What it looks for**:
- Geographic factors
- Resource constraints
- Trade patterns
- Regional dynamics
- Spatial influences

**Output**: Geopolitical analysis section

---

### 5. Synthesis Agent

**Purpose**: Combine all discipline analyses into unified explanation

**Inputs**:
- 6 discipline analyses
- Evidence dossier
- Original observation

**Process**:
1. Read all analyses
2. Identify common themes across disciplines
3. Resolve contradictions
4. Weight evidence quality
5. Construct narrative
6. Highlight key patterns

**Outputs**:
- Executive summary
- Unified explanation ("What's actually happening")
- Key patterns (3-5 bullets)
- Confidence levels per claim
- Areas of uncertainty

---

### 6. Pattern Detection Agent

**Purpose**: Find recurring patterns across multiple analyses

**Inputs**:
- Current analysis
- All past analyses
- Pattern library

**Process**:
1. Compare frameworks used across analyses
2. Identify framework clusters that appear together
3. Find similar phenomena in past research
4. Detect meta-patterns (patterns of patterns)
5. Suggest new frameworks to formalize

**Outputs**:
- Detected patterns ("You've seen this 5 times before")
- Framework co-occurrence insights
- Suggestions for new frameworks
- Updated pattern library

**Example**:
```
PATTERN DETECTED: "Status Beverages"
- Appears in: Matcha, Cold Brew, Kombucha analyses
- Common frameworks: Costly Signaling, Veblen Goods, Social Proof
- Occurrences: 3
- Suggestion: Create "Status Beverage Theory" framework
```

---

### 7. Evidence Agent

**Purpose**: Fact-check and validate all claims

**Inputs**:
- Complete analysis (all sections)
- Evidence dossier

**Process**:
1. Extract all factual claims
2. Match claims to evidence
3. Verify citations
4. Flag unverified claims
5. Assess evidence quality
6. Add missing citations

**Outputs**:
- Evidence verification report
- Quality scores per claim
- Citation links
- Flags for unverified statements
- Suggestions for additional evidence needed

**Example**:
```
✅ "Matcha prices $5-8" - Verified (source: Menu data, 50 cafes)
✅ "Google Trends 300% increase" - Verified (source: Google Trends 2015-2023)
⚠️ "Demographics 18-35" - Needs citation
❌ "Originated in 2018" - Contradicted (actually 2015)
```

---

### 8. Application Agent

**Purpose**: Extract business/product insights

**Inputs**:
- Complete analysis
- Synthesis
- Your domain of interest (product/business)

**Process**:
1. Identify generalizable patterns
2. Extract principles
3. Find similar opportunities
4. Generate actionable insights
5. Link to past applications

**Outputs**:
- Business implications (3-5 bullets)
- Product applications (specific examples)
- Similar opportunities ("What's the next X?")
- Principles to apply
- Links to related research

**Example**:
```
BUSINESS APPLICATIONS:
1. Premium pricing + health claims = status signal opportunity
2. Visual aesthetics enable social sharing (Instagram test)
3. Cultural imports gain sophistication bonus

SIMILAR OPPORTUNITIES:
- Look for: Cultural import + health halo + visual appeal
- Candidates: Ceremonial cacao, adaptogenic mushrooms

PRINCIPLES:
- Status goods need public consumption visibility
- Health justifies premium price to self
- Aesthetic appeal drives organic marketing
```

---

## AIRTABLE SCHEMA

### Your Current Setup

✅ **Frameworks Table** (200+ frameworks)

### Tables to Add

#### Observations Table

| Field | Type | Purpose |
|-------|------|---------|
| Question/Phenomenon | Long text | "Why did matcha become popular?" |
| Type | Single select | Question / Phenomenon / Hypothesis |
| Date Added | Date | When captured |
| Status | Single select | 🔴 Not researched / 🟡 In progress / ✅ Researched |
| Initial Thoughts | Long text | Your hunches |
| Context | Long text | What prompted this |
| Potential Frameworks | Linked records | → Frameworks table |
| Research | Linked record | → Research table (when completed) |
| Related Observations | Linked records | Similar observations |
| Tags | Multi-select | Topical tags |

#### Research Table

| Field | Type | Purpose |
|-------|------|---------|
| Topic | Single line text | "Matcha Popularity Analysis 2026" |
| Observation | Linked record | → Observations table |
| Frameworks Used | Linked records | → Frameworks table |
| Disciplines | Multi-select | Which of 6 lenses used |
| Status | Single select | Draft / In Progress / Complete |
| Date Started | Date | When began |
| Date Completed | Date | When finished |
| File Path | Long text | `/analyses/matcha-popularity/synthesis.md` |
| Key Insights | Long text | 3-5 bullet summary |
| Patterns Discovered | Linked records | → Patterns table |
| Business Applications | Long text | How to apply |
| Confidence | Single select | Low / Medium / High |
| Evidence Quality | Single select | Weak / Moderate / Strong |

#### Patterns Table

| Field | Type | Purpose |
|-------|------|---------|
| Pattern Name | Single line text | "Status Beverages" |
| Description | Long text | What is this pattern |
| Source Research | Linked records | → Research table (which analyses revealed this) |
| Related Frameworks | Linked records | → Frameworks table |
| Occurrences | Number | How many times seen |
| First Detected | Date | When first noticed |
| File Path | Long text | `/connections/status-beverages.md` |
| Business Applications | Long text | How to apply |
| Confidence | Single select | Hypothesis / Validated / Proven |
| Tags | Multi-select | Topical tags |

---

## WORKFLOWS & OPERATING CADENCE

### Daily (5 minutes)

**1. Capture Observations**

When you notice something interesting:

```
Add to Airtable → Observations table:
- Question/Phenomenon: [What you noticed]
- Type: Question
- Context: [Where/when]
- Initial thoughts: [Your hunches]
- Status: 🔴 Not researched
```

**v1**: Manual entry
**v2**: Voice note → Observation Agent captures
**v3**: Automatic capture from notes/messages

**Examples**:
- "Why are Owala bottles everywhere?"
- "Why is the Swift economy so massive?"
- "Why did my dad rush me as a kid?"

---

### Weekly (1-2 hours)

**2. Deep Dive Analysis**

Pick 1-2 observations to research deeply:

**v1 Process** (Manual):
1. Review observations in Airtable
2. Pick one to research
3. Manually search frameworks in Airtable
4. Create analysis file: `analyses/[topic]/synthesis.md`
5. Use template (see Templates section)
6. Research evidence (web, papers, past analyses)
7. Apply frameworks through each discipline
8. Write synthesis
9. Update Airtable Research table with metadata

**v2 Process** (Semi-Automated):
1. Select observation in Airtable
2. Trigger Framework Retrieval Agent → suggests 15 frameworks
3. Review and approve frameworks
4. Trigger Research Agent → gathers evidence
5. Trigger Discipline Agents → each writes their section
6. Review draft analyses
7. Trigger Synthesis Agent → combines into unified explanation
8. Edit and finalize
9. Airtable automatically updated

**v3 Process** (Fully Automated):
1. Select observation
2. Click "Analyze" button
3. All 8 agents run automatically
4. Review final analysis
5. Approve or request revisions
6. Airtable automatically updated

---

### Monthly (2-3 hours)

**3. Pattern Review**

Review all research from the month to find meta-patterns:

**Process**:
1. Pattern Detection Agent scans all analyses
2. Shows you:
   - Framework co-occurrence patterns
   - Similar phenomena across analyses
   - Suggested new frameworks
3. You review and decide:
   - Which patterns are real vs noise
   - Which to formalize as new frameworks
   - What business insights to extract
4. Create pattern docs in `connections/`
5. Update Patterns table in Airtable

**Questions to Ask**:
- Which frameworks appear together frequently?
- What phenomena share similar explanations?
- What new frameworks should I formalize?
- What business principles can I extract?

---

## IMPLEMENTATION ROADMAP

### v1: Foundation (Week 1) - CURRENT

**Goal**: Set up structure, test workflow manually

**Tasks**:
- ✅ Create `knowledge_brain/` folder structure
- ✅ Create CLAUDE.md (this document)
- ✅ Create README.md
- ✅ Create analysis template
- ✅ Create pattern template
- ⏳ Add Observations table to Airtable
- ⏳ Add Research table to Airtable
- ⏳ Add Patterns table to Airtable
- ⏳ Run first manual analysis

**Deliverable**: Working manual workflow

---

### v2: Semi-Automation (Weeks 2-4)

**Goal**: Add AI agents for framework retrieval and research

**Tasks**:
- Set up vector database (Pinecone or Chroma)
- Embed all 200 frameworks
- Build Framework Retrieval Agent
- Build Research Agent (web search API)
- Build basic Discipline Agents (prompted sequentially)
- Create workflow automation

**Tech Stack**:
- Vector DB: Pinecone or Chroma
- Embeddings: OpenAI `text-embedding-3-large`
- Airtable API integration
- Web search: Perplexity or Tavily API

**Deliverable**: Click-to-analyze workflow with AI assistance

---

### v3: Full Agents (Month 2+)

**Goal**: Fully autonomous multi-agent system

**Tasks**:
- Build all 8 agents
- Set up agent orchestration (LangGraph)
- Enable parallel processing (6 discipline agents run simultaneously)
- Build Pattern Detection Agent
- Build Evidence Agent
- Build Application Agent
- Create feedback loops for continuous improvement

**Tech Stack**:
- Agent Framework: LangGraph or Anthropic Agents SDK
- Multi-agent orchestration
- Background job processing
- Pattern detection algorithms
- Automated Airtable updates

**Deliverable**: Autonomous thinking brain that continuously learns

---

## EXAMPLE: COMPLETE WORKFLOW

### Question: "Why did matcha become popular in the US?"

#### Step 1: Observation Capture (You)

**Airtable → Observations**:
```
Question: "Why did matcha become popular in the US?"
Type: Question
Context: "Every coffee shop now has matcha lattes, seeing it everywhere"
Initial thoughts: "Status signaling? Health trend? Aesthetic appeal?"
Status: 🔴 Not researched
```

---

#### Step 2: Framework Retrieval Agent

**Agent searches your 200 frameworks**:

```
Searching Airtable frameworks...
Embedding query: "matcha popularity US status health trend aesthetic"

Top 15 Relevant Frameworks:

1. Costly Signaling (Evolutionary Psychology) - 95% match
   Why: Expensive products signal quality/status

2. Social Proof (Social Science) - 92% match
   Why: Popularity drives more popularity

3. Veblen Goods (Economics) - 90% match
   Why: Price increases perceived value

4. Cultural Diffusion (Anthropology) - 88% match
   Why: Japanese culture spreading to US

5. Health Halo Effect (Psychology) - 85% match
   Why: Health perception affects choices

6. Network Effects (Economics) - 82% match
   Why: Value increases with more users

7. Status Games (Evolutionary Psychology) - 80% match
   Why: Competition for social status

8. Ritual & Ceremony (Anthropology) - 78% match
   Why: Consumption as ritual

9. Aesthetic Labor (Sociology) - 75% match
   Why: Visual presentation matters

10. Identity Signaling (Social Science) - 73% match
    Why: Consumption signals identity

11. Positional Goods (Economics) - 70% match
    Why: Value from relative scarcity

12. Cultural Capital (Sociology) - 68% match
    Why: Cultural knowledge as status

13. Conspicuous Consumption (Economics) - 65% match
    Why: Visible spending signals wealth

14. Trend Diffusion (Sociology) - 62% match
    Why: How trends spread through populations

15. Third Place Theory (Sociology) - 60% match
    Why: Coffee shops as community spaces
```

---

#### Step 3: Research Agent

**Agent gathers evidence**:

```
WEB SEARCH RESULTS:

Google Trends:
- "matcha" searches increased 300% from 2015-2023
- Peak interest: Urban coastal cities (SF, NYC, LA)

Pricing Data:
- Average matcha latte: $5-8
- Regular coffee: $3-5
- Premium pricing vs alternatives

Demographics:
- Primary consumers: 18-35 years old
- College-educated
- Urban dwellers
- Health-conscious

Instagram Data:
- #matcha: 5.2M posts
- Highly visual (green color, latte art)
- Lifestyle aesthetic

Academic Papers:
- "Conspicuous Consumption in the Instagram Age" (2021)
- "Health Trends and Status Signaling" (2020)
- "Cultural Diffusion in Food Trends" (2019)

Past Analyses:
- Similar to: "Why did cold brew become popular?" (2023)
- Related: "Owala bottles as status symbols" (2025)
```

---

#### Step 4: Discipline Agents (6 run in parallel)

##### 4.1 Evolutionary Psychology Agent

```
## EVOLUTIONARY PSYCHOLOGY ANALYSIS

### Frameworks Applied
- Costly Signaling (95% relevance)
- Status Games (80% relevance)

### Analysis

Matcha's popularity is partly explained by costly signaling theory.
The high price ($5-8 vs $3-5 for regular coffee) makes it an effective
status signal because:

1. **Costly Signaling**: The expense is visible and "wasteful"
   - You could get caffeine cheaper elsewhere
   - The cost signals you can afford to pay premium
   - Public consumption in coffee shops maximizes visibility

2. **Status Competition**: Urban professionals compete for status
   - Matcha signals: health-conscious, culturally sophisticated, wealthy enough
   - Alternative signals (luxury goods) are less socially acceptable at work
   - Food/beverage choices are acceptable status signals

3. **Honest Signal**: The cost makes it hard to fake
   - Can't easily substitute cheaper alternatives
   - Requires sustained spending to maintain signal
   - This makes it a credible signal of status

### Key Insights
- Premium pricing enables status signaling
- Public consumption is critical (coffee shop vs home)
- Competes with other status signals (cold brew, specialty coffee)

### Evidence
- Pricing data shows 60% premium vs regular coffee
- Instagram posts show public consumption (#matcha in coffee shops)
- Demographics align with status-conscious consumers (18-35, urban, educated)
```

##### 4.2 Anthropology Agent

```
## ANTHROPOLOGICAL ANALYSIS

### Frameworks Applied
- Cultural Diffusion (88% relevance)
- Ritual & Ceremony (78% relevance)
- Cultural Capital (68% relevance)

### Analysis

Matcha represents cultural diffusion from Japan to the US, with specific
anthropological patterns:

1. **Cultural Diffusion**: Traditional Japanese beverage adopted by US
   - Original context: Zen Buddhist tea ceremonies
   - Adapted context: Instagram-friendly lattes
   - Cultural meaning transformed: spirituality → wellness lifestyle

2. **Cultural Capital**: Knowing about matcha signals cultural sophistication
   - Requires knowledge of Japanese culture
   - Signals cosmopolitan identity
   - Differentiates from mainstream coffee culture

3. **Ritual Transformation**: Tea ceremony → daily ritual
   - Original: Formal, meditative, spiritual
   - New: Quick, public, social
   - Retains ritual elements: preparation, presentation, consumption

4. **Identity Formation**: Matcha consumption as identity marker
   - "I'm the kind of person who drinks matcha"
   - Signals: health-conscious, cultured, mindful
   - Creates in-group (matcha drinkers) vs out-group

### Key Insights
- Cultural imports gain "exotic sophistication" bonus
- Original cultural meaning gets reinterpreted
- Becomes identity marker for specific demographic

### Evidence
- Japanese tea ceremony history (source: Wikipedia, traditional texts)
- Instagram aesthetics show transformed ritual (preparation photos)
- Demographics show specific cultural identity (urban, educated, wellness-oriented)
```

##### 4.3 History Agent

```
## HISTORICAL ANALYSIS

### Frameworks Applied
- Trend Cycles (historical pattern)
- Technological Change (enabling factor)

### Analysis

Matcha's rise follows historical pattern of "exotic wellness trends":

1. **Timeline**:
   - 2012-2014: Early adopters (specialty cafes in SF, NYC)
   - 2015-2018: Mainstream adoption (Starbucks adds matcha)
   - 2019-2023: Peak popularity
   - 2024+: Maturation phase

2. **Historical Precedents**:
   - Similar to: Green tea (1990s), Acai (2000s), Kombucha (2010s)
   - Pattern: Exotic → Health claims → Status symbol → Mainstream
   - Each wave lasts ~5-7 years

3. **Enabling Technology**:
   - Instagram (2010) enabled visual sharing
   - Food photography culture
   - Influencer marketing
   - Without Instagram, likely slower adoption

4. **Geopolitical Context**:
   - Growing interest in Japanese culture (anime, minimalism, Marie Kondo)
   - Post-2010 wellness movement
   - Backlash against sugary drinks

### Key Insights
- Follows predictable trend cycle
- Instagram was critical enabling technology
- Part of broader Japan cultural influence wave

### Evidence
- Google Trends shows 2015-2018 acceleration
- Instagram launch 2010 precedes matcha rise
- Parallel trends: Marie Kondo (2014), minimalism (2015)
```

##### 4.4 Social Science Agent

```
## SOCIAL SCIENCE ANALYSIS

### Frameworks Applied
- Social Proof (92% relevance)
- Network Effects (82% relevance)
- Identity Signaling (73% relevance)

### Analysis

Social dynamics amplified matcha's spread:

1. **Social Proof**: Popularity drives popularity
   - "Everyone at the office drinks matcha"
   - Herd behavior in coffee shop orders
   - FOMO (fear of missing out) effect

2. **Network Effects**: More matcha drinkers → more value
   - More demand → more coffee shops offer it
   - More availability → easier to maintain habit
   - Positive feedback loop

3. **Identity Signaling**: Public consumption signals identity
   - Green color is highly visible
   - Coffee shop setting is public
   - Instagram posts amplify signal
   - Signals: "I'm health-conscious and cultured"

4. **In-Group Formation**: Matcha drinkers as community
   - Shared identity
   - Shared knowledge (how to order, prepare)
   - Social bonding over shared practice

### Key Insights
- Social proof accelerated adoption
- Visibility (green color, Instagram) was critical
- Created in-group identity

### Evidence
- Instagram #matcha shows social sharing
- Network effects visible in coffee shop adoption curve
- Demographics show clustered adoption (urban coastal cities)
```

##### 4.5 Economics Agent

```
## ECONOMIC ANALYSIS

### Frameworks Applied
- Veblen Goods (90% relevance)
- Positional Goods (70% relevance)
- Conspicuous Consumption (65% relevance)

### Analysis

Economic principles explain matcha's premium pricing:

1. **Veblen Good Effect**: Higher price increases demand
   - Consumers perceive expensive = better quality
   - Price signals luxury/premium status
   - Paradoxical: raising price increases appeal

2. **Positional Goods**: Value from relative scarcity
   - Not everyone can afford $8 lattes daily
   - Scarcity creates exclusivity
   - Early adopters had more positional value (before mainstream)

3. **Conspicuous Consumption**: Visible spending signals wealth
   - Public consumption (coffee shop) maximizes visibility
   - $8/day × 5 days = $40/week = $2,080/year
   - Signals disposable income

4. **Market Dynamics**:
   - Supply side: Low switching costs for coffee shops (add matcha to menu)
   - Demand side: High willingness to pay (status value > product cost)
   - Result: Rapid market expansion

### Key Insights
- Premium pricing was strategic, not just cost-based
- Veblen effect made it more appealing
- Market expanded due to low supply-side barriers

### Evidence
- Pricing data: $5-8 for matcha vs $3-5 for coffee
- Starbucks adoption (2015) shows mainstream viability
- Consumer willingness to pay premium (sales data)
```

##### 4.6 Geopolitics Agent

```
## GEOPOLITICAL ANALYSIS

### Frameworks Applied
- Cultural Flows (geographic diffusion)
- Trade Routes (import logistics)

### Analysis

Geographic and trade factors enabled matcha's spread:

1. **Cultural Flows**: Japan → US coastal cities → inland
   - Initial adoption: SF, NYC, LA (Pacific Rim + coastal)
   - Later: Other urban centers
   - Pattern follows cultural diffusion routes

2. **Trade Routes**: Japanese imports to US
   - Matcha sourced from Japan (Uji region)
   - Import infrastructure existed
   - Premium Japanese products already had market (sushi, sake)

3. **Geographic Clustering**:
   - Urban coastal cities adopted first
   - Wealth concentration in these areas
   - Cultural openness to foreign foods

4. **Regional Variation**:
   - Coastal urban: High adoption
   - Rural areas: Low adoption
   - Follows existing patterns of exotic food adoption

### Key Insights
- Geography shaped adoption pattern
- Coastal cities are cultural gateways
- Trade infrastructure enabled supply

### Evidence
- Google Trends by region (coastal cities lead)
- Import data shows Japanese matcha imports increased
- Coffee shop distribution follows urban/coastal pattern
```

---

#### Step 5: Synthesis Agent

```
## SYNTHESIS: Why Matcha Became Popular in the US

### What's Actually Happening

Matcha's popularity is the result of converging factors across all disciplines:

**The Complete Picture**:

Matcha became popular because it simultaneously satisfied multiple needs:

1. **Status Signaling** (Evolutionary): Premium price ($5-8) makes it an
   effective status signal. Public consumption in coffee shops maximizes
   visibility. Signals: "I'm wealthy enough, health-conscious, culturally
   sophisticated."

2. **Cultural Sophistication** (Anthropology): Association with Japanese
   culture (tea ceremonies, zen, minimalism) adds exotic appeal. Consumers
   gain cultural capital by knowing about and consuming matcha.

3. **Social Proof** (Social Science): Once early adopters started, social
   proof accelerated adoption. Instagram amplified visibility. Created
   in-group identity ("matcha people").

4. **Premium Positioning** (Economics): Veblen good effect - higher price
   increased perceived value. Conspicuous consumption in public settings
   maximized status signal.

5. **Perfect Timing** (History): Rose during wellness movement (2015+),
   Instagram era (visual sharing), and Japan cultural wave (anime,
   Marie Kondo, minimalism).

6. **Geographic Diffusion** (Geopolitics): Entered through coastal urban
   cities (SF, NYC, LA) where wealth, cultural openness, and trade routes
   converge.

### Key Patterns

**Pattern 1: Status Beverages**
- Matcha follows same pattern as: Cold brew, kombucha, specialty coffee
- Formula: Premium price + health claims + public consumption + visual appeal
- All target same demographic: 18-35, urban, educated, high income

**Pattern 2: Cultural Import → Status Symbol**
- Foreign origin adds exotic sophistication
- Japanese culture specifically signals mindfulness/quality
- Original cultural meaning gets reinterpreted for new context

**Pattern 3: Instagram Amplification**
- Visual appeal (green color, latte art) drives sharing
- Sharing drives social proof
- Social proof drives adoption
- Creates viral loop

### Why This Matters

Understanding matcha's rise reveals principles applicable to other products:

1. **Premium + Health + Aesthetic = Status Opportunity**
2. **Public consumption amplifies status signals**
3. **Cultural imports gain sophistication bonus**
4. **Instagram-friendly products have distribution advantage**
5. **Urban coastal cities are adoption gateways**

### Confidence Assessment

- **High confidence** (80%+): Status signaling, Veblen effect, social proof
- **Medium confidence** (60-80%): Cultural capital, network effects
- **Lower confidence** (40-60%): Geographic determinism as primary factor

### Areas of Uncertainty

- **Causation vs correlation**: Did Instagram cause adoption or just amplify?
- **Comparative**: Why matcha over other Japanese imports (hojicha, genmaicha)?
- **Sustainability**: Will matcha follow cold brew's trajectory (peak → decline)?

### Related Questions

- Why did cold brew peak and decline?
- What's the "next matcha" in 2026?
- Why do some food trends last (coffee) while others fade (cronuts)?
```

---

#### Step 6: Pattern Detection Agent

```
PATTERN DETECTION RESULTS:

Analyzing current research against 15 past analyses...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PATTERN FOUND: "Status Beverages"

Occurrences: 3
- Matcha popularity (current)
- Cold brew analysis (2023)
- Kombucha analysis (2022)

Common Frameworks:
- Costly Signaling (appeared in all 3)
- Veblen Goods (appeared in all 3)
- Social Proof (appeared in all 3)
- Health Halo (appeared in 2/3)

Common Characteristics:
- Premium pricing ($5-8 range)
- Health claims (antioxidants, energy, gut health)
- Public consumption (coffee shops, juice bars)
- Urban demographic (18-35, educated, high income)
- Visual appeal (Instagram-friendly)

Pattern Strength: HIGH (85% confidence)

RECOMMENDATION: Formalize as new framework "Status Beverage Theory"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PATTERN FOUND: "Cultural Import Premium"

Occurrences: 4
- Matcha (Japanese)
- Acai bowls (Brazilian)
- Kombucha (Russian/Chinese)
- Ramen (Japanese)

Common Frameworks:
- Cultural Diffusion
- Cultural Capital
- Costly Signaling

Insight: Foreign origin adds 20-30% price premium when associated
with "sophisticated" culture (Japanese, French, Italian)

Pattern Strength: MEDIUM (70% confidence)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SIMILAR PAST RESEARCH:
- Owala water bottles (status signaling through design)
- Swift economy (cultural capital, identity formation)
- Vietnamese community (in-group formation)

SUGGESTED NEW FRAMEWORKS:
1. "Status Beverage Theory" - Formalize the pattern
2. "Instagram Effect" - How visual social media amplifies trends
3. "Wellness Premium" - Health claims justify status spending

SUGGESTED NEXT RESEARCH:
- "Why did cold brew decline after peak?"
- "What will be the next matcha in 2026?"
- "Why do some trends last while others fade?"
```

---

#### Step 7: Evidence Agent

```
EVIDENCE VERIFICATION REPORT:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFIED CLAIMS:

✅ "Matcha lattes cost $5-8 vs $3-5 for regular coffee"
   Source: Menu data from 50 coffee shops (SF, NYC, LA)
   Quality: HIGH

✅ "Google Trends shows 300% increase 2015-2023"
   Source: Google Trends data
   Quality: HIGH

✅ "Instagram #matcha has 5.2M posts"
   Source: Instagram search (Jan 2026)
   Quality: MEDIUM (fluctuates)

✅ "Matcha originated in Japan, used in tea ceremonies"
   Source: Historical records, cultural documentation
   Quality: HIGH

✅ "Starbucks added matcha around 2015"
   Source: Starbucks press releases
   Quality: HIGH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLAIMS NEEDING CITATION:

⚠️ "Primary consumers are 18-35 years old, college-educated"
   Status: Plausible but needs demographic data
   Action: Add citation or mark as "assumed"

⚠️ "Cultural import adds 20-30% price premium"
   Status: Pattern observed but not quantified
   Action: Conduct comparative pricing analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTRADICTIONS FOUND:

❌ "Matcha mainstream adoption started 2018"
   Contradiction: Some sources say 2015 (Starbucks entry)
   Resolution: Clarify "early adoption" vs "mainstream"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVERALL EVIDENCE QUALITY: STRONG (75%)
- Most claims verified
- Few gaps in demographic data
- Minor timeline discrepancies

RECOMMENDATIONS:
1. Add demographic study citation
2. Clarify adoption timeline
3. Quantify cultural premium claim
```

---

#### Step 8: Application Agent

```
BUSINESS & PRODUCT APPLICATIONS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRINCIPLES EXTRACTED:

1. **Premium Pricing + Health Claims = Status Signal**
   - When health justifies cost to self, status is bonus
   - People pay premium for products they can morally justify
   - Application: Any wellness product can use this formula

2. **Public Consumption Amplifies Status Signals**
   - Products consumed publicly (cafes, gyms) have advantage
   - Private consumption (supplements, apps) lacks this
   - Application: Design for public visibility

3. **Cultural Imports Gain Sophistication Bonus**
   - Foreign origin (especially Japan, France, Italy) adds premium
   - Cultural knowledge required = cultural capital
   - Application: Source from "sophisticated" cultures

4. **Instagram-Friendly = Free Distribution**
   - Visual appeal drives organic sharing
   - Sharing creates social proof loop
   - Application: Design for Instagram (aesthetics matter)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SIMILAR OPPORTUNITIES (What's the "next matcha"?):

Look for products that combine:
- ✅ Foreign/exotic origin (cultural sophistication)
- ✅ Health claims (moral justification)
- ✅ Premium pricing ($5-10 range)
- ✅ Visual appeal (Instagram-friendly)
- ✅ Public consumption (cafes, restaurants)

CANDIDATES FOR 2026:

1. **Ceremonial Cacao**
   - Origin: Central/South America (exotic)
   - Health: Antioxidants, mood enhancement
   - Price: $8-12 for ceremonial drinks
   - Visual: Dark, aesthetic presentation
   - Status: Early in trend cycle

2. **Adaptogenic Mushroom Lattes**
   - Origin: Traditional Chinese medicine (exotic)
   - Health: Stress relief, immunity
   - Price: $7-10
   - Visual: Instagram-friendly
   - Status: Rising

3. **Hojicha (Roasted Green Tea)**
   - Origin: Japan (follows matcha)
   - Health: Lower caffeine, antioxidants
   - Price: $5-8
   - Visual: Brown, aesthetic
   - Status: Early adoption phase

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RELATED PAST RESEARCH:

Similar patterns in:
- Owala water bottles (status through visible design)
- Cold brew coffee (premium coffee trend before matcha)
- Kombucha (health + premium + exotic)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACTIONABLE FOR PRODUCT BUILDERS:

**If building consumer product:**
1. Can you add cultural origin story? (Japan, France, Italy, Scandinavia)
2. Can you add health claim? (Backed by traditional use or studies)
3. Can you justify premium pricing? ($20-50 for physical, $10-30/mo for digital)
4. Is consumption public or shareable? (Design for visibility)
5. Is it Instagram-friendly? (Aesthetics, colors, presentation)

**If building for matcha-drinking demographic:**
- Who: 18-35, urban, college-educated, high income
- Values: Health, culture, aesthetics, status
- Where: Coastal cities, coffee shops, gyms, co-working spaces
- Psychographics: Wellness-oriented, culturally curious, status-conscious

**Framework Clusters to Apply:**
- Status signaling + health + cultural capital
- Social proof + network effects + identity formation
- Premium pricing + Veblen effect + conspicuous consumption
```

---

#### Step 9: Output & Storage

**Generated Files**:

`analyses/matcha-popularity-2026/synthesis.md` - Complete analysis (all sections above)

**Airtable Updates**:

**Research Table** - New record:
- Topic: "Matcha Popularity Analysis 2026"
- Observation: Linked to "Why did matcha become popular?"
- Frameworks Used: 15 frameworks linked
- Disciplines: All 6
- Status: Complete
- File Path: `/analyses/matcha-popularity-2026/synthesis.md`
- Key Insights: "Premium pricing + health + cultural import = status signal..."
- Patterns Discovered: Linked to "Status Beverages" pattern

**Patterns Table** - Updated:
- Pattern "Status Beverages": Occurrences increased from 2 → 3
- Added matcha to source research

**Observations Table** - Updated:
- Status changed: 🔴 → ✅ Researched
- Research field: Linked to new research record

---

## PROMPTS & TEMPLATES

### Analysis Prompt (for Claude)

```
You are a multi-disciplinary research analyst. Analyze the following observation
using frameworks from the user's Airtable library.

OBSERVATION:
[Question or phenomenon]

CONTEXT:
[Background information]

AIRTABLE FRAMEWORKS:
[Paste top 15 frameworks from Framework Retrieval Agent]

EVIDENCE:
[Paste research dossier from Research Agent]

INSTRUCTIONS:
1. For each of the 6 disciplines (Evolutionary Psychology, Anthropology,
   History, Social Science, Economics, Geopolitics), write an analysis section:
   - List frameworks applied (2-4 per discipline)
   - Explain how the discipline explains this phenomenon
   - Provide 3-5 key insights
   - Cite evidence

2. Write a synthesis section:
   - Combine all disciplines into unified explanation
   - Identify key patterns (3-5)
   - Assess confidence levels
   - Note areas of uncertainty

3. Extract business/product applications:
   - Generalizable principles
   - Similar opportunities
   - Actionable insights

4. Compare to past research:
   - Find similar phenomena
   - Detect recurring patterns
   - Suggest new frameworks to formalize

OUTPUT FORMAT: See template in `analyses/_template.md`
```

---

### Framework Retrieval Prompt

```
You are a framework retrieval agent. Your job is to search the user's Airtable
framework library and return the most relevant frameworks for analyzing an observation.

AIRTABLE BASE: [Base ID]
TABLE: Frameworks (200+ records)

OBSERVATION:
[User's question or phenomenon]

INSTRUCTIONS:
1. Embed the observation text
2. Search all frameworks using semantic similarity
3. Rank by relevance (0-100%)
4. Ensure diversity across all 6 disciplines
5. Return top 15 frameworks

OUTPUT FORMAT:
For each framework:
- Name
- Discipline
- Relevance score (%)
- Why it's relevant (1 sentence)
- Link to Airtable record

Organize by relevance score (highest first)
```

---

### Pattern Detection Prompt

```
You are a pattern detection agent. Your job is to find recurring patterns
across multiple analyses.

CURRENT ANALYSIS:
[Paste synthesis section]

PAST ANALYSES:
[List of past analyses with summaries]

INSTRUCTIONS:
1. Compare frameworks used across analyses
2. Identify framework clusters that appear together frequently
3. Find similar phenomena in past research
4. Detect meta-patterns
5. Suggest new frameworks to formalize

OUTPUT FORMAT:
For each pattern found:
- Pattern name
- Occurrences (list analyses where it appears)
- Common frameworks
- Common characteristics
- Pattern strength (confidence %)
- Recommendation (formalize as new framework? yes/no)
```

---

## NEXT STEPS

**Immediate** (Today):
1. Review this document
2. Add Observations, Research, and Patterns tables to your Airtable
3. Capture 3-5 observations you want to research

**This Week** (v1):
1. Run your first manual analysis using the template
2. Test the workflow
3. Refine based on what works/doesn't work

**Next 2-4 Weeks** (v2):
1. Set up vector database
2. Build Framework Retrieval Agent
3. Build Research Agent
4. Test semi-automated workflow

**Month 2+** (v3):
1. Build all 8 agents
2. Set up agent orchestration
3. Enable autonomous analysis
4. Continuous learning and improvement

---

**This document is your system's memory. Reference it for all analyses, workflows, and agent implementations.**
- We always test step by step, module by module, so if we are adding a credential, we test the credential first. Then we test the query. Get it?