"""
Demographics & Market Analysis - Forno SSR Analysis
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Demographics", page_icon="📍", layout="wide")

st.title("📍 King Street Demographics & Market Analysis")
st.markdown("**Location:** Forno Cultura, King & Portland, Toronto")

# Overview
st.markdown("## Market Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Entertainment District Residents",
        value="30,000+",
        delta="Condo-heavy demographics"
    )

with col2:
    st.metric(
        label="Anchor Tenant",
        value="Shopify",
        delta="Next door at King-Portland Centre"
    )

with col3:
    st.metric(
        label="Primary Transit",
        value="504 King Streetcar",
        delta="High foot traffic corridor"
    )

# Acquisition channels
st.markdown("---")
st.markdown("## Acquisition Channels")

st.markdown("""
King Street draws customers from 3 primary channels:
""")

channel1, channel2, channel3 = st.columns(3)

with channel1:
    st.markdown("""
    ### 🏢 Office Workers
    **Primary channel**

    **Sources:**
    - Shopify (King-Portland Centre, 602-620 King W)
    - King West startups/agencies
    - Financial District commuters (10 min walk)

    **Session types:**
    - Morning coffee grab (7:30-9am)
    - Lunch rush (12-2pm)
    - Coffee chat meetings (10am-2pm)

    **Subscription fit:**
    - ✅ Sandwich + Coffee Pass (lunch regulars)
    - ✅ Morning Commuter Pass (grab-and-go)
    """)

with channel2:
    st.markdown("""
    ### 🏠 Condo Residents
    **Growing channel**

    **Demographics:**
    - 30,000+ Entertainment District residents
    - Small kitchens (650-900 sq ft condos)
    - Young professionals (25-40)
    - Outsource meal prep

    **Session types:**
    - Workday laptop (10am-4pm, Mon/Fri heavy)
    - Weekend bread ritual (Sat/Sun)
    - Evening pickup (5-7pm dinner)

    **Subscription fit:**
    - ✅ Bread & Pantry Box (meal replacement)
    - ✅ Weekend Loop (bread ritual)
    """)

with channel3:
    st.markdown("""
    ### 🚇 Transit Commuters
    **Opportunistic channel**

    **Sources:**
    - 504 King streetcar
    - Financial District (subway + walk)
    - Suburban commuters (evening pickup)

    **Session types:**
    - Morning commute (7:30-9am)
    - Post-work pickup (5-7pm)

    **Subscription fit:**
    - ⚠️ Lower intent (sporadic visits)
    - Better for: Morning pass, Evening pickup
    """)

# Session types
st.markdown("---")
st.markdown("## Session Type Framework")

st.markdown("""
Based on Queen West analysis, we identified **7 distinct session types** at King Street:
""")

# Session type chart
session_data = {
    "Session Type": [
        "Morning Commute",
        "Workday Laptop",
        "Lunch Rush",
        "Coffee Chat",
        "Post-Work Pickup",
        "Weekend Loop",
        "Mixed/Frequent"
    ],
    "Time Slot": [
        "7:30-9am",
        "10am-4pm Mon/Fri",
        "12-2pm",
        "10am-2pm",
        "5-7pm",
        "Sat/Sun",
        "All day"
    ],
    "Persona Count": [1, 2, 2, 1, 1, 4, 3],
    "Best Subscription": [
        "Underground Regulars Club",
        "Sandwich + Coffee Pass",
        "Sandwich + Coffee Pass",
        "Sandwich + Coffee Pass",
        "Sandwich + Coffee Pass",
        "Sandwich + Coffee Pass",
        "Varies"
    ]
}

st.dataframe(
    session_data,
    use_container_width=True,
    hide_index=True
)

# Temporal patterns
st.markdown("---")
st.markdown("## Temporal Patterns")

st.markdown("""
### Weekday vs Weekend Dynamics

**Weekday (Mon-Fri):**
- Morning rush: 7:30-9am (commuters, Shopify workers)
- Mid-morning laptop: 10am-12pm (remote workers, freelancers)
- Lunch peak: 12-2pm (office workers, meetings)
- Afternoon laptop: 2-4pm (condo residents)
- Evening pickup: 5-7pm (commuters grabbing dinner)

**Weekend (Sat-Sun):**
- Weekend bread ritual: 9am-2pm (residents, destination visitors)
- Brunch crowd: 10am-2pm (Entertainment District visitors)

**Hybrid Work Impact:**
- Mon/Fri: Higher laptop session volume (remote workers)
- Wed: Higher office worker volume (peak office day)
""")

# Create temporal pattern visualization
temporal_fig = go.Figure()

temporal_fig.add_trace(go.Bar(
    name="Weekday",
    x=["7:30-9am", "10am-12pm", "12-2pm", "2-4pm", "5-7pm"],
    y=[40, 25, 50, 30, 35],
    marker_color="#3498db"
))

temporal_fig.add_trace(go.Bar(
    name="Weekend",
    x=["9am-11am", "11am-2pm"],
    y=[35, 45],
    marker_color="#2ecc71"
))

temporal_fig.update_layout(
    title="Estimated Traffic Distribution by Time Slot",
    xaxis_title="Time Slot",
    yaxis_title="Relative Volume",
    height=400,
    barmode="group"
)

st.plotly_chart(temporal_fig, use_container_width=True)

# Shopify opportunity
st.markdown("---")
st.markdown("## 🎯 Shopify Proximity Advantage")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### The Opportunity

    **Shopify's King-Portland Centre** (602-620 King West) is literally **next door** to Forno.

    **Walking distance:**
    - Shopify to Forno: **1 minute** walk
    - Financial District to Forno: **10 minutes** walk

    **Impact on subscription intent:**
    - **p11 (Shopify worker):** 3.84/5.0 (HIGHEST of all personas)
    - **p9 (Financial District):** 3.31/5.0 (54 basis points lower)

    **Physical proximity dramatically increases subscription intent.**

    ### B2B Corporate Partnership

    **Pitch to Shopify People Ops:**
    - "Healthier team lunch alternative"
    - Discounted bulk rate: $100/month (vs $120 retail)
    - Pilot: 50 employees
    - Revenue potential: $5,000/month recurring

    **Positioning:**
    - Skip catered lunch logistics
    - Support local business
    - Fresh, quality meals daily
    - Employee chooses their sandwich/coffee days
    """)

with col2:
    # Proximity impact chart
    proximity_fig = go.Figure(data=[
        go.Bar(
            x=["Shopify\n(1 min walk)", "Financial District\n(10 min walk)"],
            y=[3.84, 3.31],
            marker_color=["#2ecc71", "#e74c3c"],
            text=["3.84", "3.31"],
            textposition="outside"
        )
    ])

    proximity_fig.update_layout(
        title="Proximity Impact on Intent",
        yaxis_title="Subscription Intent (1-5)",
        yaxis_range=[0, 5],
        height=400,
        showlegend=False
    )
    proximity_fig.add_hline(y=3.0, line_dash="dash", line_color="gray")

    st.plotly_chart(proximity_fig, use_container_width=True)

# Income level analysis
st.markdown("---")
st.markdown("## Income Level vs Subscription Intent")

income_data = {
    "Income Level": ["Affluent", "Comfortable", "Managing/Struggling"],
    "Sandwich + Coffee Pass": [3.60, 3.52, 2.91],
    "Bread & Pantry Box": [3.29, 3.15, 2.93],
    "Underground Regulars Club": [3.26, 3.42, 2.97]
}

col1, col2 = st.columns([2, 1])

with col1:
    # Create grouped bar chart
    income_fig = go.Figure()

    for concept in ["Sandwich + Coffee Pass", "Bread & Pantry Box", "Underground Regulars Club"]:
        income_fig.add_trace(go.Bar(
            name=concept,
            x=income_data["Income Level"],
            y=income_data[concept]
        ))

    income_fig.update_layout(
        title="Subscription Intent by Income Level",
        xaxis_title="Income Level",
        yaxis_title="Mean Rating (1-5)",
        yaxis_range=[0, 5],
        height=400,
        barmode="group"
    )
    income_fig.add_hline(y=3.0, line_dash="dash", line_color="gray")

    st.plotly_chart(income_fig, use_container_width=True)

with col2:
    st.markdown("""
    ### Key Insights

    **Affluent customers prefer:**
    - Meal-focused subscriptions (Sandwich Pass, Bread Box)
    - Higher willingness to pay for convenience

    **Mid-income customers:**
    - Value Regulars Club discount more than wealthy
    - Still strong intent for Sandwich Pass

    **Lower-income visitors:**
    - Can't justify ANY subscription
    - Sporadic visitors, not daily regulars
    - Better to target with one-off promotions
    """)

st.markdown("---")
st.caption("King West demographic insights inform persona selection and subscription positioning →")
