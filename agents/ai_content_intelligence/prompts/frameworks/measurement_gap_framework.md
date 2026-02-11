# Measurement Gap Framework

Use this framework to analyze how AI products should be measured differently from pre-AI products.

## Context

You are analyzing products through the lens of: **"The Measurement Gap"**

**Core thesis:** Growth loops are changing. Most teams are still measuring the old ones. Analytics teams are still measuring growth the way they did pre-AI — funnels, conversion rates, DAU/MAU, feature adoption. These metrics were designed for a world where growth was linear. AI changed the loops. But the dashboards didn't update.

**The 5 Measurement Failures:**
1. **Teams measure AI adoption. They should measure behavior replacement.** — What % of users stopped doing the old thing because AI works better?
2. **The insight plateau is killing retention — and dashboards can't see it.** — When do insights stop being new, and does the product know?
3. **AI features improve products but don't grow them.** — Did anyone discover us *because* of what the AI produced?
4. **Teams measure time-in-app. Best AI products measure time-to-done.** — How fast did the user accomplish what they came to do?
5. **Standard growth metrics miss AI-specific leading indicators.** — What early signals predict whether AI will compound growth?

---

## Analysis Structure

### Part 1: Current Measurement Baseline

For this product, identify what the team likely measures today:

**Standard Metrics In Use:**
- Acquisition: [e.g., signups, viral coefficient, attribution]
- Activation: [e.g., time to first value, onboarding completion]
- Engagement: [e.g., DAU/MAU, session length, feature adoption]
- Retention: [e.g., monthly churn, retention curves]
- Revenue: [e.g., upgrade rate, LTV, expansion]

**AI-Specific Metrics (if any):**
- AI feature adoption rate
- AI engagement metrics
- AI satisfaction/NPS

**Evidence:** What public signals suggest these are the metrics? (Blog posts, job descriptions, product updates, user dashboards)

---

### Part 2: Map Measurement Failures to This Product

For each of the 5 measurement failures, assess relevance:

#### Failure #1: Measuring Adoption Instead of Behavior Replacement

**Relevance:** High / Medium / Low / None

**What they likely measure:**
- "% of users who tried AI feature"
- "AI feature usage frequency"

**What they should measure:**
- **Behavior Replacement Rate (BRR):** What % of users stopped doing the old workflow because AI replaced it?
- **Workflow displacement:** Did AI add to their workflow or replace steps?

**Evidence from research:**
- User quotes showing replacement: [quote]
- User quotes showing augmentation: [quote]
- User quotes showing non-adoption: [quote]

**The metric gap:**
[Specific description of what's invisible in current metrics but visible in replacement measurement]

---

#### Failure #2: Missing the Insight Plateau

**Relevance:** High / Medium / Low / None

**What they likely measure:**
- Monthly retention
- App opens
- Engagement frequency

**What they should measure:**
- **Time-to-Insight-Plateau (TIP):** When do insights stop being novel?
- **Insight engagement depth:** Are users reading/acting on insights or just glancing at scores?
- **Learning velocity:** How fast do users internalize patterns vs. how fast the product provides new ones?

**Evidence from research:**
- User quotes showing plateau: [quote showing "I know my patterns now"]
- User quotes showing ongoing discovery: [quote showing "still learning new things"]

**The metric gap:**
[What current dashboards show vs. what's actually happening with insight value decay]

---

#### Failure #3: AI Features Don't Equal AI Growth Loops

**Relevance:** High / Medium / Low / None

**What they likely measure:**
- AI feature usage
- Satisfaction with AI outputs
- Engagement lift from AI

**What they should measure:**
- **AI-Attributed Discovery Rate:** What % of new users found the product because they saw what the AI produced?
- **AI output shareability:** How much AI output escapes the product boundary?
- **External visibility:** Can non-users see that users got better/faster?

**Evidence from research:**
- Is AI output inherently visible? [e.g., Wispr = yes, Notion = no]
- User quotes about sharing AI results: [quote]
- Social proof of AI output: [screenshots, posts, UGC]

**The metric gap:**
[Difference between "AI improved experience for existing users" vs. "AI brought new users"]

---

#### Failure #4: Time-in-App vs. Time-to-Done

**Relevance:** High / Medium / Low / None

**What they likely measure:**
- Session length
- DAU/MAU
- Time-in-app
- Screens per session

**What they should measure:**
- **Time-to-Core-Action (TCA):** How long from intent to completion?
- **Cross-app activation:** Does value delivery require opening the app?
- **Invisible usage:** Value delivered without the user "being" in the product?

**Evidence from research:**
- User quotes about speed: [quote about how fast they get things done]
- User quotes about friction: [quote about steps required]
- Workflow integration depth: [layer vs. destination positioning]

**The metric gap:**
[Why shorter sessions might mean better product, not worse engagement]

---

#### Failure #5: Missing AI-Specific Leading Indicators

**Relevance:** High / Medium / Low / None

**Standard lagging metrics:**
- Monthly retention
- Churn rate
- Upgrade rate (measured at end of trial/month)

**AI-specific leading indicators to add:**
- **Early behavior replacement signal:** Did user stop the old workflow in week 1?
- **AI dependency velocity:** How fast does AI become part of muscle memory?
- **Cognitive switching cost:** What would it take for the user to go back to the old way?
- **Output velocity delta:** How much faster/better did the user become in first 14 days?

**Evidence from research:**
- User quotes showing dependency: [quote about "can't imagine going back"]
- User quotes showing optionality: [quote about "use it sometimes"]

**The metric gap:**
[What early signals predict long-term retention that current dashboards miss]

---

### Part 3: The Experiment to Run

Based on the measurement failures identified, design ONE high-impact experiment:

**Experiment Name:** [Descriptive title]

**Hypothesis:** [What you believe is true but can't prove with current metrics]

**Setup:**
- **Cohort definition:** [How to segment users]
- **Measurement window:** [Time period]
- **Key metric:** [The new metric you're testing]
- **Success criteria:** [What would prove the hypothesis]

**Why this experiment matters:**
[Connection to business decisions — what would the team do differently if they knew this?]

---

### Part 4: The Dashboard Redesign

If you were Head of Product Analytics for this product, what would you change?

**Metrics to deprecate:**
- [Standard metric that misleads]
- [Why it's misleading for AI products]

**Metrics to add:**
- [New AI-specific metric]
- [Why it reveals hidden dynamics]

**New dashboards to build:**
- **AI Growth Loop Dashboard:** Separates "AI improves product" from "AI drives growth"
- **Behavior Replacement Tracker:** Monitors workflow displacement, not just feature adoption
- **Insight Engagement Depth:** Measures novelty decay, not just app opens

---

### Part 5: What This Reveals About AI Measurement

**Core insight:** [One sentence: What does this product reveal about how AI should be measured?]

**Portable pattern:** [Can other products use this measurement approach? In which categories?]

**What's measurable now:** [Which metrics could be instrumented today with existing data?]

**What requires new instrumentation:** [Which metrics need new event tracking?]

**What changes with this data:** [How would product/growth decisions shift if these metrics existed?]

---

### Part 6: Carousel Angles

Based on this analysis, suggest 2-3 potential carousel angles:

**Angle 1:**
- Hook concept: [One sentence that stops scroll]
- Core argument: [What you're proving about measurement gaps]
- Measurement failures highlighted: [Which of the 5]
- Why it matters: [Why builders should care]

**Angle 2:**
[Repeat structure]

**Angle 3:**
[Repeat structure]

---

## Output Requirements

Your analysis should be:

- **Specific:** Use product details from research, not generic observations
- **Evidence-based:** Point to actual user quotes showing measurement gaps
- **Actionable:** Every metric proposed should be instrumentable
- **Business-grounded:** Connect measurement gaps to actual decisions teams make
- **Insight-driven:** Show what this reveals about AI measurement broadly

**Avoid:**
- Generic analytics advice ("track everything")
- Metrics that sound impressive but aren't actionable
- Speculation without evidence from research
- Measurement for measurement's sake (every metric should inform a decision)

**Remember:**
The goal isn't to measure more. It's to measure what matters for AI products — the signals that standard dashboards miss but actually predict whether AI compounds growth.
