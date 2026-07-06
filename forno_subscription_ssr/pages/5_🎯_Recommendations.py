"""
Recommendations - Forno SSR Analysis
"""

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Recommendations", page_icon="🎯", layout="wide")

st.title("🎯 Recommendations & Next Steps")
st.markdown("**Actionable roadmap based on SSR findings**")

# Executive recommendation
st.markdown("## Executive Recommendation")

st.success("""
### Two-Track Launch Strategy

Based on SSR findings, we recommend a **dual-track approach** that targets both B2C and B2B segments simultaneously:

1. **Track 1 (B2B):** Shopify corporate partnership - Faster revenue, proven demand
2. **Track 2 (B2C):** Public Sandwich + Coffee Pass - Broader market validation

This approach de-risks the launch while maximizing revenue potential.
""")

# Detailed recommendations
st.markdown("---")
st.markdown("## Detailed Recommendations")

# Track 1: B2B Shopify
st.markdown("### 🤝 Track 1: Shopify Corporate Partnership")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **Target:** Shopify People Ops at King-Portland Centre (602-620 King West)

    **Pitch:**
    - "Healthier team lunch alternative for 50 employees"
    - Fresh, quality meals from local bakery next door
    - Flexible subscription (employees choose their days)
    - No catering logistics required

    **Pricing:**
    - $100/month per employee (discounted from $120 retail)
    - Includes: 8 sandwiches + 8 coffees per month
    - Company pays, employees redeem

    **Revenue Potential:**
    - 50 employees × $100/month = **$5,000 MRR**
    - If 100 employees: **$10,000 MRR**

    **Why it works:**
    - p11 (Shopify worker) showed HIGHEST intent (3.84/5.0)
    - 1-minute walk = captive lunch audience
    - Shopify values supporting local businesses
    - No commute/logistics hassle for employees
    """)

with col2:
    # Revenue projection
    shopify_fig = go.Figure()

    shopify_fig.add_trace(go.Bar(
        name="25 employees",
        x=["Month 1"],
        y=[2500],
        marker_color="#3498db"
    ))

    shopify_fig.add_trace(go.Bar(
        name="50 employees",
        x=["Month 1"],
        y=[5000],
        marker_color="#2ecc71"
    ))

    shopify_fig.add_trace(go.Bar(
        name="100 employees",
        x=["Month 1"],
        y=[10000],
        marker_color="#f39c12"
    ))

    shopify_fig.update_layout(
        title="Shopify Partnership Revenue Scenarios",
        yaxis_title="Monthly Recurring Revenue ($)",
        height=350,
        barmode="group"
    )

    st.plotly_chart(shopify_fig, use_container_width=True)

    st.info("""
    **Timeline:**
    - Week 1-2: Secure warm intro
    - Week 3-4: Pitch + negotiations
    - Month 2: Pilot launch (25-50 employees)
    - Month 3-4: Evaluate + scale
    """)

# Track 2: B2C Public
st.markdown("---")
st.markdown("### 🎯 Track 2: Public B2C Launch")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **Concept:** King West Sandwich + Coffee Pass

    **Target Segments:**
    - King West office workers (p1: 3.76/5.0)
    - Hybrid laptop workers (p5: 3.56/5.0)
    - Individual Shopify employees (p11: 3.84/5.0)
    - Coffee chat professionals (p10: 3.59/5.0)

    **Pricing:**
    - $120/month (retail price)
    - Includes: 8 sandwiches + 8 coffees
    - 2 visits per week, perfect for hybrid workers

    **Marketing Channels:**
    - In-store signage at Forno King Street
    - LinkedIn posts (target King West workers)
    - Instagram stories (tag King-Portland Centre, King West)
    - Partner with nearby coworking spaces

    **Value Proposition:**
    - "Skip the lunch line, guaranteed fresh panini"
    - "Your regular order, always ready"
    - "Support local, save time, eat better"

    **Launch KPIs:**
    - Month 1: 20+ signups
    - Month 2: 70%+ retention
    - Month 3: 50+ active subscribers
    """)

with col2:
    # Growth projection
    growth_fig = go.Figure()

    growth_fig.add_trace(go.Scatter(
        x=["Month 1", "Month 2", "Month 3", "Month 6"],
        y=[20, 35, 50, 100],
        mode="lines+markers+text",
        marker=dict(size=12, color="#2ecc71"),
        line=dict(width=3, color="#2ecc71"),
        text=[20, 35, 50, 100],
        textposition="top center",
        name="Conservative"
    ))

    growth_fig.add_trace(go.Scatter(
        x=["Month 1", "Month 2", "Month 3", "Month 6"],
        y=[30, 60, 90, 150],
        mode="lines+markers+text",
        marker=dict(size=12, color="#3498db"),
        line=dict(width=3, color="#3498db", dash="dash"),
        text=[30, 60, 90, 150],
        textposition="top center",
        name="Optimistic"
    ))

    growth_fig.update_layout(
        title="B2C Subscriber Growth Projections",
        yaxis_title="Active Subscribers",
        height=350
    )

    st.plotly_chart(growth_fig, use_container_width=True)

    st.info("""
    **Revenue at 50 subscribers:**
    - 50 × $120 = **$6,000 MRR**

    **Combined with Shopify (50 employees):**
    - Total: **$11,000 MRR**
    """)

# Additional subscription opportunities
st.markdown("---")
st.markdown("## Additional Subscription Opportunities")

opp1, opp2, opp3 = st.columns(3)

with opp1:
    st.markdown("""
    ### ☕ Morning Commuter Pass

    **Why:** Underground Regulars Club won 7:30-9am slot (3.46/5.0)

    **Design:**
    - 20 coffees + 10 pastries/month
    - $80/month
    - Grab-and-go focus, no lunch items

    **Target:**
    - Financial District commuters (p9)
    - Early Shopify arrivals
    - 504 streetcar riders

    **Launch:** Month 5-6 (after Sandwich Pass validated)
    """)

with opp2:
    st.markdown("""
    ### 🥖 Bread & Pantry Box

    **Why:** Strong niche fit for condo residents (3.40/5.0)

    **Design:**
    - Weekly artisan bread + pantry staples
    - $140/month
    - Meal replacement positioning

    **Target:**
    - Condo residents with small kitchens (p12)
    - Evening pickup customers (p13)
    - Weekend bread ritual (p2, p4)

    **Market:** 30,000 Entertainment District residents

    **Launch:** Month 6+ (niche play after mass market validated)
    """)

with opp3:
    st.markdown("""
    ### 🎭 Underground Regulars Club

    **Why:** Broad appeal but shallow depth (3.22/5.0)

    **Status:** Hold as "lite" tier

    **Design:**
    - 15% discount on all purchases
    - Skip-the-line perk
    - $40/month

    **Use case:**
    - Entry-level subscription
    - Lower-frequency visitors
    - "Upgrade path" from one-time customers

    **Launch:** Month 9+ (after higher-value subscriptions proven)
    """)

# Implementation timeline
st.markdown("---")
st.markdown("## Implementation Timeline")

timeline_data = {
    "Phase": [
        "Phase 1: Shopify Validation",
        "Phase 1: Shopify Validation",
        "Phase 1: Shopify Validation",
        "Phase 2: Public Launch",
        "Phase 2: Public Launch",
        "Phase 2: Public Launch",
        "Phase 3: Portfolio Expansion",
        "Phase 3: Portfolio Expansion"
    ],
    "Activity": [
        "Reach out to Shopify People Ops",
        "Pitch + negotiate corporate deal",
        "Run 3-month pilot (25-50 employees)",
        "Launch Sandwich + Coffee Pass (public)",
        "Target 20+ signups month 1",
        "Monitor retention + engagement",
        "Add Morning Commuter Pass (if demand)",
        "Add Bread Box (if condo interest)"
    ],
    "Timeline": [
        "Week 1-2",
        "Week 3-4",
        "Month 2-4",
        "Month 2",
        "Month 2-3",
        "Month 3-4",
        "Month 5-6",
        "Month 6+"
    ],
    "KPI": [
        "Warm intro secured",
        "Pilot approved",
        "Signup rate, retention",
        "Public launch live",
        "20+ subscribers",
        "70%+ retention",
        "Morning demand validated",
        "Condo resident signups"
    ]
}

st.dataframe(
    timeline_data,
    use_container_width=True,
    hide_index=True
)

# Success metrics
st.markdown("---")
st.markdown("## Success Metrics & Decision Gates")

st.markdown("""
### Month 3 Review

**Metrics to measure:**
- Shopify: Signup rate (% of offered employees), retention month-to-month
- B2C: Total subscribers, retention rate, add-on spend per visit
- Combined MRR

**Decision:**
- If Shopify pilot succeeds (50%+ signup, 80%+ retention) → Expand to more employees
- If B2C hits 50+ subscribers → Scale marketing, prepare Morning Pass
- If both underperform → Pivot pricing or messaging

---

### Month 6 Review

**Metrics:**
- Total MRR from subscriptions
- Customer acquisition cost (CAC)
- Lifetime value (LTV)
- Net Promoter Score (NPS)

**Decision:**
- If MRR > $10K → Expand portfolio (Morning Pass, Bread Box)
- If MRR $5-10K → Double down on what's working
- If MRR < $5K → Reassess concept or target market

---

### Month 12 Goal

**Target:** $15-20K MRR from subscriptions
- Shopify corporate: $5-10K
- B2C Sandwich Pass: $6-8K
- Morning Pass / Bread Box: $2-3K
""")

# Risk mitigation
st.markdown("---")
st.markdown("## Risk Mitigation")

risk1, risk2 = st.columns(2)

with risk1:
    st.warning("""
    ### Risk 1: Shopify says no

    **Mitigation:**
    - Have B2C launch ready regardless
    - Target other King West employers (agencies, startups)
    - Focus on individual Shopify employees via B2C

    **Fallback:** B2C-only launch still viable based on strong individual intent
    """)

    st.warning("""
    ### Risk 3: Retention below 70%

    **Mitigation:**
    - Survey churned customers immediately
    - Test pricing adjustments ($100/month)
    - Add flexibility (pause/resume, rollover credits)

    **Decision gate:** If retention < 50% by Month 3, pause new signups and fix retention first
    """)

with risk2:
    st.warning("""
    ### Risk 2: Low B2C signups (< 20 in Month 1)

    **Mitigation:**
    - Offer launch promo ($99 first month)
    - Partner with King West coworking spaces (free trial)
    - Host "Subscriber Appreciation Day" (exclusive menu item)

    **Pivot:** If organic signups low, consider corporate-only strategy
    """)

    st.warning("""
    ### Risk 4: Operational capacity

    **Mitigation:**
    - Cap initial signups at 100 total
    - Monitor peak hour demand patterns
    - Hire additional staff if needed

    **Scaling plan:** Add capacity incrementally (100 → 200 → 300 subscribers)
    """)

# Final CTA
st.markdown("---")
st.success("""
## Next Action

**Immediate next step:** Secure warm introduction to Shopify People Ops

**Potential paths:**
1. Through King-Portland Centre building management
2. Via existing Shopify customers at Forno
3. LinkedIn outreach to Shopify HR team
4. Through Shopify employee referral (p11 persona type)

**Timing:** Reach out within 2 weeks while analysis is fresh

**Goal:** Pitch meeting scheduled within 1 month
""")

st.markdown("---")
st.caption("This analysis cost $1.68 in API calls and revealed a $5-10K/month revenue opportunity. Ship it. →")
