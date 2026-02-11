# Knowledge Brain

**A multi-disciplinary thinking system for understanding human behavior**

---

## What This Is

A research workspace that helps you:
- Apply your 200+ frameworks (stored in Airtable) to understand phenomena
- Analyze questions through 6 disciplines (Evolutionary Psychology, Anthropology, History, Social Science, Economics, Geopolitics)
- Detect patterns across analyses
- Extract business/product insights

---

## Quick Start (5 Minutes)

### 1. Capture an Observation

When you notice something interesting, add it to Airtable → Observations table:

**Examples**:
- "Why did matcha become popular?"
- "Why are Owala bottles everywhere?"
- "Why is the Swift economy so massive?"

### 2. Research It

Create an analysis file using the template in `analyses/_template.md`:
1. Select 10-15 relevant frameworks from your Airtable
2. Apply each discipline's lens (6 total)
3. Synthesize findings
4. Extract business applications

### 3. Update Airtable

Add metadata to Research table:
- Link to observation
- Link to frameworks used
- Add key insights (3-5 bullets)
- Add file path

### 4. Find Patterns

Monthly: Review all analyses to spot recurring patterns
- Which frameworks appear together?
- What phenomena share similar explanations?
- What business principles emerge?

---

## File Structure

```
knowledge_brain/
├── CLAUDE.md                    # Complete system architecture (read this!)
├── README.md                    # This file
├── analyses/
│   ├── _template.md            # Multi-lens analysis template
│   └── [your-analyses]/
│       └── synthesis.md
├── connections/
│   ├── _template.md            # Pattern documentation template
│   └── [pattern-name].md
└── outputs/
    ├── case_studies/           # Published case studies
    └── reports/                # Phenomenon explanations
```

---

## Your Airtable Setup

### Existing:
✅ **Frameworks table** (200+ frameworks)

### To Add:
- **Observations table** - Capture questions/phenomena
- **Research table** - Track completed analyses (metadata)
- **Patterns table** - Document recurring patterns

See `CLAUDE.md` for detailed schema.

---

## The 6 Disciplines

Every analysis applies these lenses:

1. **Evolutionary Psychology** - Why do humans behave this way?
2. **Anthropology** - How do cultures organize?
3. **History** - What historical factors matter?
4. **Social Science** - How do societies function?
5. **Economics** - What incentives drive behavior?
6. **Geopolitics** - How does geography shape behavior?

---

## Example Workflow

**Question**: "Why did matcha become popular?"

**Step 1**: Add to Airtable Observations
- Question: "Why did matcha become popular in the US?"
- Context: "Every coffee shop has matcha lattes now"
- Status: 🔴 Not researched

**Step 2**: Select Frameworks (from your Airtable)
- Costly Signaling (Evolutionary Psychology)
- Cultural Diffusion (Anthropology)
- Trend Cycles (History)
- Social Proof (Social Science)
- Veblen Goods (Economics)
- Cultural Flows (Geopolitics)

**Step 3**: Research & Analyze
- Gather evidence (web search, papers, data)
- Apply each discipline's lens
- Write analysis using template

**Step 4**: Synthesize
- Combine all 6 analyses
- Find key patterns
- Extract business insights

**Step 5**: Update Airtable
- Add to Research table
- Link frameworks used
- Document insights

---

## Agent Roadmap

### v1 (Week 1) - Manual
You do everything manually with templates

### v2 (Weeks 2-4) - Semi-Automated
- Framework Retrieval Agent suggests relevant frameworks
- Research Agent gathers evidence
- Discipline Agents draft sections

### v3 (Month 2+) - Fully Agentic
- 8 specialized agents work autonomously
- You just capture observations and validate outputs
- Continuous pattern detection

See `CLAUDE.md` for complete agent architecture.

---

## Next Steps

1. **Read** `CLAUDE.md` for complete system details
2. **Add** Observations, Research, and Patterns tables to Airtable
3. **Capture** 3-5 observations you want to research
4. **Run** your first analysis using `analyses/_template.md`

---

## Key Principle

**Frameworks in Airtable (source of truth) → Apply to observations (markdown analysis) → Detect patterns (connections)**

Your 200 frameworks are the foundation. Every analysis references them. Over time, patterns emerge and new frameworks form.

---

**Questions?** See `CLAUDE.md` for detailed architecture, workflows, and agent designs.
