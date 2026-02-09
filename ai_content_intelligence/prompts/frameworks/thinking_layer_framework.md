# Thinking Layer Framework

Use this framework to demonstrate how better thinking produces better analysis — even with the same AI tools.

## Context

You are analyzing products through the lens of: **"The Thinking Layer"**

**Core thesis:** AI can do the analysis. It can't do the thinking. Everyone has access to the same AI tools now. The same models, the same speed, the same ability to generate cohort charts, run SQL, and build dashboards in seconds. The difference isn't the tool. It's what you ask it to do.

Pillar 3 shows this live — each post takes a real product situation, grounds it in actual user quotes and public data, applies a specific thinking skill to reframe the problem, and then demonstrates how that reframe changes the AI output from generic to strategic.

The implicit message: **the thinking directed the AI, not the other way around. And that thinking is the part that doesn't get commoditized.**

---

## What Makes Pillar 3 Different From Growth Consulting Content

Two things separate this from what any smart generalist could write:

### 1. The Product Analytics Layer

Every post goes beyond "here's the metric I'd track" into the **how** — event taxonomy design, data model thinking, instrumentation specifics. The language of someone who's *built* analytics infrastructure (Segment, BigQuery, Amplitude, Looker), not someone who reads dashboards others built.

Examples:
- **Wispr:** Voice-to-typed ratio as a behavioral event tracked at user level over time — derivable from `input_method` event property, not a survey
- **Oura:** Insight engagement depth as an event property (`insight_depth: glance | explore | deep_dive`) on `score_viewed` event
- **Todoist:** Capture windows from `task_created` timestamps — time-series analysis revealing behavioral expansion, no new tracking required
- **Notion:** Full event schema (`content_origin_type`, `paste_with_formatting_detection`, `ai_interaction_depth`, `time_to_first_content`)

This is the difference between "measure retention better" and "here's the event taxonomy that makes retention *mean* something."

### 2. The AI-as-Thinking-Partner Layer

The AI angle goes deeper than "better prompt = better output." Each post shows AI being used *inside the analytical workflow* — not as a search engine but as a reasoning partner:

- Pressure-testing behavioral hypotheses
- Modeling what data *should* look like before you have it
- Stress-testing instrumentation design
- Generating counter-hypotheses the analyst might be blind to

The reader sees someone *reasoning with* AI the way they'd reason with a sharp colleague.

---

**The 4 Thinking Skills:**
1. **Decomposition** — Aggregate metrics hide distinct behaviors with different retention trajectories (Wispr: voice-to-typed ratio)
2. **Inversion** — Ask "under what conditions would this stop working?" instead of "why is this working?" (Oura: insight_depth)
3. **Second-order thinking** — Ask "what does this make possible, and what does that change?" (Todoist: capture windows)
4. **Reframe the unit of analysis** — Same data, different question, different insight (Notion: content_origin)

---

## Analysis Structure

### Part 1: User Quotes as Raw Material

Start with 2-3 contrasting user quotes from research that reveal behavioral divergence:

**Quote 1: [User segment A]**
> "[Actual user quote from research]"

**Quote 2: [User segment B]**
> "[Actual user quote from research]"

**Quote 3: [User segment C - if relevant]**
> "[Actual user quote from research]"

**Source:** [Where these quotes came from: Reddit, reviews, Product Hunt, etc.]

**Initial observation:** [What do these quotes reveal at surface level?]

---

### Part 2: The Obvious Question (First-Order Frame)

What would most teams ask when seeing this data?

**Standard analyst frame:**
"[The obvious question that comes from looking at the quotes]"

**What this frame produces:**
- [Typical insight #1]
- [Typical insight #2]
- [Typical recommendation]

**The generic AI prompt:**
```
"Analyze these user quotes and identify the key themes. What are users saying about [product]?"
```

**Generic AI output:**
[Show what this prompt typically produces — surface-level themes, no depth]

---

### Part 3: The Reframe (Thinking Skill Applied)

**Thinking skill:** [Choose one: Decomposition, Inversion, Second-order, First-principles, or Reframe unit of analysis]

**The sharper question:**
"[The question that emerges from applying the thinking skill to the same quotes]"

**Why this question is different:**
[One sentence explaining how the thinking skill changes what you're looking for]

**What this reveals:**
[The insight that only emerges from the reframed question — something the obvious frame was blind to]

---

### Part 4: The AI Prompt Comparison

**Prompt A: Generic Frame**
```
[The obvious prompt most analysts would use]
```

**Output from Prompt A:**
```
[Generic, surface-level analysis]
```

---

**Prompt B: Reframed with Thinking Skill**
```
[The prompt that encodes the sharper thinking — specific instructions about what patterns to look for, what assumptions to question, what hidden dynamics to surface]
```

**Output from Prompt B:**
```
[Strategic, actionable analysis that surfaces dynamics the generic prompt missed]
```

---

**The difference:**
[Explicit comparison showing:
- Same quotes
- Same AI tool
- Different thinking = different insight quality
- The thinking directed the tool, not the other way around]

---

### Part 5: What This Surfaces (Strategic Implications + Instrumentation)

The reframed analysis reveals:

**Leading indicators:**
[Early signals that predict future behavior, trackable now]

**Behavioral patterns:**
[User segments with different trajectories hidden in aggregate metrics]

**Competitive dynamics:**
[Where the product is vulnerable or defensible based on user behavior, not features]

**Product decisions this informs:**
- [Decision 1]
- [Decision 2]
- [Decision 3]

**CRITICAL: Event Taxonomy & Instrumentation Details**

This is where the product analytics differentiation lands. Include specific:

**Event schema:**
- Event names (e.g., `score_viewed`, `task_created`, `content_pasted`)
- Event properties (e.g., `insight_depth: glance | explore | deep_dive`)
- Derived metrics (e.g., voice-to-typed ratio from `input_method` property)

**Data model thinking:**
- What's derivable from existing events (no new instrumentation)
- What requires new event properties
- How to compute the metric at user-session level
- Cohort segmentation logic

**Instrumentation specifics:**
- Stack references (Segment, BigQuery, Amplitude, Looker)
- Time-series analysis requirements
- Edge cases the schema needs to handle
- How this would show up in production dashboards

**Example instrumentation detail:**
"The voice-to-typed ratio isn't a survey — it's derivable from existing product telemetry. You'd instrument `input_method` on every text event and compute the ratio at the user-session level. The cohort segmentation writes itself from there."

**Why the standard frame missed this:**
[What assumption or mental model prevented the obvious question from seeing this?]

---

### Part 6: Where Else This Applies

Show transferability — apply the same thinking skill to other common metrics/situations:

**Example 1: [Common metric/situation]**
- Standard frame: [What most teams ask]
- Reframe with [thinking skill]: [What the sharper question reveals]
- Insight gained: [What becomes visible]

**Example 2: [Common metric/situation]**
- Standard frame: [What most teams ask]
- Reframe with [thinking skill]: [What the sharper question reveals]
- Insight gained: [What becomes visible]

**Example 3: [Common metric/situation - if relevant]**
- Standard frame: [What most teams ask]
- Reframe with [thinking skill]: [What the sharper question reveals]
- Insight gained: [What becomes visible]

---

### Part 7: Why This Matters (The Moat Message)

**Closing observation:**

[One paragraph that lands the thesis implicitly:
- AI can answer any first-order question in seconds
- The thinking that goes deeper is the part that produces insight a team actually acts on
- Same tool, different thinking, different strategic value
- This is the part that doesn't get commoditized

No preaching — the reader just watched it happen.]

---

### Part 8: Carousel Angles

Based on this analysis, suggest 1-2 potential carousel angles:

**Angle 1:**
- Title: [Hook that names the hidden pattern]
- Core argument: [What you're proving about thinking with AI]
- Thinking skill demonstrated: [Which of the 5]
- Reader takeaway: [What they can apply to their own analysis]

**Angle 2:**
[Repeat structure]

---

## Tone and Style Rules

**What to do:**
- Lead with the user quotes — make the analysis grounded in real behavior
- Name the thinking skill lightly (one line, woven in naturally — not a lesson header)
- Show the AI prompt comparison honestly (acknowledge what you don't have access to — the power is in the question, not the data)
- **Show the analytics stack when relevant** — Segment, BigQuery, Amplitude, event properties, SQL, cohort segmentation. This is the language that separates the product analyst from the growth consultant.
- **Show AI as reasoning partner, not search engine** — the reframed prompts don't just "ask better questions." They provide behavioral structures and ask AI to help surface implications, pressure-test hypotheses, and generate analytical artifacts (retention curves, event schemas, SQL queries).
- Personal experience is one data point, not an authority claim (e.g., Notion post uses "my own pattern" as one of three data points)
- The closing lands the moat message implicitly — the reader just watched the thinking happen

**What to avoid:**
- Don't start with "Here's a mental model lesson..."
- Don't pretend to have internal data you don't have — work from public quotes and be explicit about it
- Don't prescribe "you should build this metric" — instead: "here's the event taxonomy that would surface it"
- No "if I were Head of Analytics" framing
- Don't preach the moat message — let the reader see it

**The reader's internal narrative should be:**
"Same quotes. Same AI tool. Her question was different. The insight quality was different. She works with AI as an analytical partner. And she can build the data architecture that makes it all visible. The thinking + instrumentation is the part that matters."

---

## Output Requirements

Your analysis should be:

- **Grounded:** Start with real user quotes from research, not hypotheticals
- **Honest:** Work from public data and be explicit about limitations
- **Demonstrative:** Show the thinking in action, don't teach it as theory
- **Transferable:** Prove the skill works on other common situations
- **Implicit:** The moat message should land through demonstration, not explanation

**Avoid:**
- Generic AI vs. human debates
- Claiming insider access to data you don't have
- Teaching mental models as lessons
- Prescriptive "here's what you should do" framing
- Preaching about the value of thinking (show, don't tell)

**Remember:**
The goal is to make the reader think: "She asks better questions than anyone on my team — she works with AI as an analytical partner — and she can build the data architecture that makes those insights visible. The thinking + instrumentation is the moat."

---

## How Pillar 3 Connects to Pillars 1 and 2

**The Escalation in Depth:**

- **Pillar 1 (Teardowns):** Observation — "Here's what's actually happening with this product's growth." Pattern recognition. → *"She sees growth loops I can't see."*

- **Pillar 2 (Measurement):** Measurement — "Here's what the standard metrics miss and what you'd need to track instead." Analytical rigor. → *"She knows what to measure that I'm not measuring."*

- **Pillar 3 (Thinking + Instrumentation):** Thinking + execution — "Here's the reframe that changes the question, the AI workflow that accelerates the analysis, and the event schema that would surface it in production data." Full stack: thinking skill → AI collaboration → data architecture. → *"She thinks differently AND she can build the systems that make those insights visible. This isn't just strategy — it's executable."*

**The Multi-Pillar Arc per Product:**

| App | Pillar 1 (The Loop) | Pillar 2 (The Metric Gap) | Pillar 3 (The Thinking + Instrumentation) |
|-----|----------|----------|----------|
| Wispr | How it actually grows | Behavior replacement rate | Decomposition — 4.7 stars hiding 3 products → voice-to-typed ratio event schema |
| Oura | How it actually grows | Insight engagement decay | Inversion — success causing churn → insight_depth event property |
| Todoist | How it actually grows | Time-to-core-action | Second-order — 5x is the start, not the answer → capture window time-series |
| Notion | How it actually grows | AI-attributed growth | Unit of analysis — adoption ≠ cognitive workflow → content_origin event taxonomy |

**Total series: 12 posts. 4 apps × 3 pillars.**

Each post stands alone. Together they build an argument that's impossible to ignore.

---

## Positioning Payoff

**What this signals to the ICP** (post-PMF companies $1M-$20M integrating AI):

The content doesn't say "hire me." The content demonstrates:
- She can look at our product and see behavioral patterns our team is blind to
- She knows what metrics we should be tracking that we're not — and she can design the event schemas to surface them
- She thinks with AI in a way that makes both sharper — and that's a workflow, not a prompt trick
- She's built these systems before (the instrumentation specifics make that obvious)

**The ICP's internal monologue:**
"We have AI tools. We have dashboards. We have analysts who can write SQL. What we don't have is someone who thinks like this — and who can turn that thinking into instrumentation our team would actually ship. Maybe she should look at our product."

**The content IS the sales pitch without pitching.**
