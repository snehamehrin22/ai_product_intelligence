"""
Personas - Forno SSR Analysis
"""

import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from forno_ssr.personas import get_all_personas, get_persona_by_id

st.set_page_config(page_title="Personas", page_icon="👥", layout="wide")

st.title("👥 Customer Personas")
st.markdown("**14 King Street customer types tested in this study**")

# Load personas and results
@st.cache_data
def load_results():
    data_dir = Path(__file__).parent.parent / "data"
    agg_files = sorted(data_dir.glob("aggregated_results_*.json"))
    if not agg_files:
        return None

    with open(agg_files[-1]) as f:
        return json.load(f)

personas = get_all_personas()
data = load_results()

if data:
    df = pd.DataFrame(data)
else:
    df = None

# Overview
st.markdown("## Overview")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    This study tested **14 personas** representing different customer types at Forno King Street:

    **Original 8 personas:**
    - Core customer segments identified in initial analysis
    - Covered: tech workers, creatives, students, couples, remote workers, locals, fitness enthusiasts, foodies

    **New 6 personas (Added June 15, 2026):**
    - Discovered through King West demographic analysis
    - Session type gaps: morning commute, coffee chat, evening pickup
    - Key opportunity: Shopify worker proximity advantage
    """)

with col2:
    if df is not None:
        # Show persona count by new vs original
        persona_type = ["Original"] * 8 + ["New"] * 6
        fig = go.Figure(data=[go.Pie(
            labels=["Original 8", "New 6"],
            values=[8, 6],
            marker_colors=["#3498db", "#2ecc71"],
            hole=0.4
        )])
        fig.update_layout(
            title="Persona Mix",
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

# Persona selector
st.markdown("---")
st.markdown("## Persona Profiles")

# Create tabs for filtering
tab1, tab2, tab3 = st.tabs(["All Personas", "Original 8", "New 6"])

with tab1:
    selected_personas = personas

with tab2:
    selected_personas = [p for p in personas if int(p.persona_id[1:]) <= 8]

with tab3:
    selected_personas = [p for p in personas if int(p.persona_id[1:]) > 8]

# Display personas
for persona in selected_personas:
    with st.expander(f"**{persona.persona_id.upper()}: {persona.age}yo {persona.role}**", expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"""
            **Age:** {persona.age}

            **Role:** {persona.role}

            **Income Level:** {persona.income_level.value}

            **Visit Frequency:** {persona.visit_frequency}

            **Current Behavior:**
            {persona.current_behavior}

            **Location/Context:** {persona.location}
            """)

        with col2:
            if df is not None:
                # Get ratings for this persona
                persona_data = df[df["persona_id"] == persona.persona_id]

                if len(persona_data) > 0:
                    # Create bar chart of concept ratings
                    concept_names = {
                        "c1": "Sandwich +\nCoffee Pass",
                        "c2": "Bread &\nPantry Box",
                        "c3": "Underground\nRegulars Club"
                    }

                    ratings = []
                    concepts = []
                    for _, row in persona_data.iterrows():
                        concepts.append(concept_names.get(row["concept_id"], row["concept_id"]))
                        ratings.append(row["avg_mean_rating"])

                    fig = go.Figure(data=[
                        go.Bar(
                            x=concepts,
                            y=ratings,
                            marker_color=["#ff6b6b", "#4ecdc4", "#45b7d1"],
                            text=[f"{r:.2f}" for r in ratings],
                            textposition="outside"
                        )
                    ])

                    fig.update_layout(
                        title=f"{persona.persona_id.upper()} Subscription Intent",
                        yaxis_title="Rating (1-5)",
                        yaxis_range=[0, 5],
                        height=300,
                        showlegend=False
                    )
                    fig.add_hline(y=3.0, line_dash="dash", line_color="gray")

                    st.plotly_chart(fig, use_container_width=True)

                    # Show best fit
                    best_concept_idx = ratings.index(max(ratings))
                    best_concept = list(concept_names.values())[best_concept_idx]
                    best_rating = max(ratings)

                    if best_rating >= 3.5:
                        st.success(f"✅ **Best fit:** {best_concept} ({best_rating:.2f}/5.0)")
                    elif best_rating >= 3.0:
                        st.info(f"🤔 **Best fit:** {best_concept} ({best_rating:.2f}/5.0)")
                    else:
                        st.warning(f"⚠️ **Best fit:** {best_concept} ({best_rating:.2f}/5.0) - Low intent")

# Highlight key personas
st.markdown("---")
st.markdown("## 🌟 Key Personas to Watch")

highlight1, highlight2, highlight3 = st.columns(3)

with highlight1:
    st.markdown("""
    ### p11: Shopify Worker
    **Highest subscription intent of all personas (3.84/5.0)**

    - 28yo product designer
    - Works next door at King-Portland Centre
    - Daily coffee, 2-3 lunches/week
    - 1-minute walk = captive lunch audience

    **Opportunity:** Corporate partnership with Shopify HR
    """)

with highlight2:
    st.markdown("""
    ### p1: King West Startup Worker
    **Strong lunch pass fit (3.76/5.0)**

    - 27yo software engineer
    - 3-4 lunches/week
    - Values speed and quality
    - Represents core lunch rush segment

    **Opportunity:** Public B2C launch target
    """)

with highlight3:
    st.markdown("""
    ### p12: Condo Resident (Remote)
    **Validates Bread Box positioning (3.40/5.0)**

    - 32yo marketing manager
    - Fully remote, 650 sq ft condo
    - Small kitchen, outsources meals
    - Represents 30K Entertainment District residents

    **Opportunity:** Meal replacement positioning
    """)

# Session type mapping
st.markdown("---")
st.markdown("## Session Type Classification")

st.markdown("""
Personas are mapped to **session types** based on their visit patterns:
""")

session_mapping = {
    "Morning Commute (7:30-9am)": ["p9"],
    "Workday Laptop (10am-4pm, Mon/Fri heavy)": ["p5", "p12"],
    "Lunch Rush (12-2pm, office workers)": ["p1", "p11"],
    "Coffee Chat (10am-2pm, business meetings)": ["p10"],
    "Post-Work Pickup (5-7pm, take-home dinner)": ["p13"],
    "Weekend Loop (Sat/Sun, bread ritual)": ["p2", "p4", "p6", "p14"],
    "Mixed/Frequent (multiple session types)": ["p3", "p7", "p8"]
}

for session_type, persona_ids in session_mapping.items():
    with st.expander(f"**{session_type}**"):
        for pid in persona_ids:
            p = get_persona_by_id(pid)
            if p:
                st.markdown(f"- **{pid.upper()}:** {p.age}yo {p.role}")

st.markdown("---")
st.caption("Use session type classification to understand which subscriptions work for which usage patterns →")
