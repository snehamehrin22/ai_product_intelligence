"""
Results & Analysis - Forno SSR Analysis
"""

import streamlit as st
import json
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from forno_ssr.personas import get_all_personas
from forno_ssr.concepts import get_all_concepts

st.set_page_config(page_title="Results & Analysis", page_icon="📈", layout="wide")

st.title("📈 Results & Analysis")
st.markdown("**Detailed findings from SSR study (14 personas × 3 concepts)**")

# Load data
@st.cache_data
def load_results():
    data_dir = Path(__file__).parent.parent / "data"
    agg_files = sorted(data_dir.glob("aggregated_results_*.json"))
    if not agg_files:
        return None

    with open(agg_files[-1]) as f:
        return json.load(f)

data = load_results()

if data is None:
    st.error("No analysis data found. Run `python scripts/run_survey.py` first.")
    st.stop()

df = pd.DataFrame(data)
personas = get_all_personas()
concepts = get_all_concepts()

# Concept name mapping
concept_names = {c.concept_id: c.name for c in concepts}

# Overall results
st.markdown("## Overall Results")

col1, col2, col3 = st.columns(3)

concept_means = df.groupby("concept_id")["avg_mean_rating"].mean()

with col1:
    st.metric(
        label="Sandwich + Coffee Pass",
        value=f"{concept_means['c1']:.2f}/5.0",
        delta="Winner"
    )

with col2:
    st.metric(
        label="Bread & Pantry Box",
        value=f"{concept_means['c2']:.2f}/5.0",
        delta=f"{concept_means['c2'] - concept_means['c1']:.2f} vs winner"
    )

with col3:
    st.metric(
        label="Underground Regulars Club",
        value=f"{concept_means['c3']:.2f}/5.0",
        delta=f"{concept_means['c3'] - concept_means['c1']:.2f} vs winner"
    )

# Interactive heatmap
st.markdown("---")
st.markdown("## Persona × Concept Heatmap")

st.markdown("Interactive heatmap showing subscription intent across all persona-concept combinations:")

# Prepare heatmap data
heatmap_data = df.pivot(index="persona_id", columns="concept_id", values="avg_mean_rating")

# Reorder
persona_order = [p.persona_id for p in personas]
concept_order = [c.concept_id for c in concepts]
heatmap_data = heatmap_data.reindex(index=persona_order, columns=concept_order)

# Create persona labels
persona_labels = [f"{p.persona_id}: {p.age}yo {p.role[:20]}..." for p in personas]

# Create heatmap
heatmap_fig = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=[concept_names[c] for c in heatmap_data.columns],
    y=persona_labels,
    colorscale="RdYlGn",
    zmid=3.0,
    zmin=1.0,
    zmax=5.0,
    text=heatmap_data.values,
    texttemplate="%{text:.2f}",
    textfont={"size": 10},
    colorbar=dict(title="Rating (1-5)")
))

heatmap_fig.update_layout(
    title="Subscription Intent by Persona and Concept",
    xaxis_title="Subscription Concept",
    yaxis_title="Customer Persona",
    height=700,
    font=dict(size=10)
)

st.plotly_chart(heatmap_fig, use_container_width=True)

# Highlight top personas for each concept
st.markdown("---")
st.markdown("## Top Personas by Concept")

tab1, tab2, tab3 = st.tabs([
    "Sandwich + Coffee Pass",
    "Bread & Pantry Box",
    "Underground Regulars Club"
])

with tab1:
    c1_data = df[df["concept_id"] == "c1"].nlargest(5, "avg_mean_rating")

    st.markdown("### Top 5 Personas - Sandwich + Coffee Pass")

    for idx, row in c1_data.iterrows():
        p = next((p for p in personas if p.persona_id == row["persona_id"]), None)
        if p:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**#{c1_data.index.get_loc(idx) + 1}**")
                with col2:
                    st.markdown(f"**{p.persona_id.upper()}:** {p.age}yo {p.role}")
                    st.caption(p.visit_frequency)
                with col3:
                    st.metric("Rating", f"{row['avg_mean_rating']:.2f}")

with tab2:
    c2_data = df[df["concept_id"] == "c2"].nlargest(5, "avg_mean_rating")

    st.markdown("### Top 5 Personas - Bread & Pantry Box")

    for idx, row in c2_data.iterrows():
        p = next((p for p in personas if p.persona_id == row["persona_id"]), None)
        if p:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**#{c2_data.index.get_loc(idx) + 1}**")
                with col2:
                    st.markdown(f"**{p.persona_id.upper()}:** {p.age}yo {p.role}")
                    st.caption(p.visit_frequency)
                with col3:
                    st.metric("Rating", f"{row['avg_mean_rating']:.2f}")

with tab3:
    c3_data = df[df["concept_id"] == "c3"].nlargest(5, "avg_mean_rating")

    st.markdown("### Top 5 Personas - Underground Regulars Club")

    for idx, row in c3_data.iterrows():
        p = next((p for p in personas if p.persona_id == row["persona_id"]), None)
        if p:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**#{c3_data.index.get_loc(idx) + 1}**")
                with col2:
                    st.markdown(f"**{p.persona_id.upper()}:** {p.age}yo {p.role}")
                    st.caption(p.visit_frequency)
                with col3:
                    st.metric("Rating", f"{row['avg_mean_rating']:.2f}")

# Session type analysis
st.markdown("---")
st.markdown("## Session Type Analysis")

st.markdown("""
Which subscription works best for different usage patterns?
""")

# Session type mapping
session_mapping = {
    "morning_commute": ["p9"],
    "workday_laptop": ["p5", "p12"],
    "lunch_rush": ["p1", "p11"],
    "coffee_chat": ["p10"],
    "post_work_pickup": ["p13"],
    "weekend_loop": ["p2", "p4", "p6", "p14"],
    "mixed_frequent": ["p3", "p7", "p8"]
}

# Add session type to dataframe
persona_to_session = {}
for session_type, persona_ids in session_mapping.items():
    for pid in persona_ids:
        persona_to_session[pid] = session_type

df["session_type"] = df["persona_id"].map(persona_to_session)

# Calculate mean by session type
session_means = df.groupby(["session_type", "concept_id"])["avg_mean_rating"].mean().reset_index()

# Create session type labels
session_labels = {
    "morning_commute": "Morning Commute\n(7:30-9am)",
    "workday_laptop": "Workday Laptop\n(10am-4pm Mon/Fri)",
    "lunch_rush": "Lunch Rush\n(12-2pm Office)",
    "coffee_chat": "Coffee Chat\n(10am-2pm Meetings)",
    "post_work_pickup": "Post-Work Pickup\n(5-7pm Dinner)",
    "weekend_loop": "Weekend Loop\n(Sat/Sun Bread)",
    "mixed_frequent": "Mixed/Frequent"
}

session_means["session_label"] = session_means["session_type"].map(session_labels)
session_means["concept_name"] = session_means["concept_id"].map(concept_names)

# Create grouped bar chart
session_fig = px.bar(
    session_means,
    x="session_label",
    y="avg_mean_rating",
    color="concept_name",
    barmode="group",
    title="Subscription Intent by Session Type",
    labels={
        "session_label": "Session Type",
        "avg_mean_rating": "Mean Rating (1-5)",
        "concept_name": "Concept"
    },
    height=500,
    color_discrete_map={
        "King West Sandwich + Coffee Pass": "#ff6b6b",
        "King West Bread & Pantry Box": "#4ecdc4",
        "Underground Regulars Club": "#45b7d1"
    }
)

session_fig.add_hline(y=3.0, line_dash="dash", line_color="gray", annotation_text="Neutral")
session_fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

st.plotly_chart(session_fig, use_container_width=True)

# Key temporal insights
st.markdown("### Key Temporal Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("""
    ✅ **Morning (7:30-9am)**

    Winner: Underground Regulars Club (3.46)

    Fast coffee + pastry discount > lunch-focused pass
    """)

with col2:
    st.success("""
    ✅ **Lunch (12-2pm)**

    Winner: Sandwich + Coffee Pass (3.62)

    Designed for this exact use case
    """)

with col3:
    st.success("""
    ✅ **Weekend (Sat/Sun)**

    Winner: Sandwich + Coffee Pass (3.36)

    Versatile across multiple session types
    """)

# Distribution analysis
st.markdown("---")
st.markdown("## Probability Distribution Analysis")

st.markdown("""
How certain are personas about their subscription intent? (Based on SSR probability distributions)
""")

# Select concept to view
selected_concept = st.selectbox(
    "Select concept to view distribution:",
    options=[c.concept_id for c in concepts],
    format_func=lambda x: concept_names[x]
)

# Get data for selected concept
concept_data = [d for d in data if d["concept_id"] == selected_concept]

# Average probability distribution
avg_probs = {str(i): 0 for i in range(1, 6)}
for d in concept_data:
    for rating in range(1, 6):
        avg_probs[str(rating)] += d["avg_probability_distribution"][str(rating)]

# Normalize
total = len(concept_data)
avg_probs = {k: v / total for k, v in avg_probs.items()}

# Create distribution chart
dist_fig = go.Figure(data=[
    go.Bar(
        x=list(avg_probs.keys()),
        y=list(avg_probs.values()),
        marker_color=["#e74c3c", "#e67e22", "#f39c12", "#2ecc71", "#27ae60"],
        text=[f"{v:.2f}" for v in avg_probs.values()],
        textposition="outside"
    )
])

dist_fig.update_layout(
    title=f"Probability Distribution - {concept_names[selected_concept]}",
    xaxis_title="Subscription Intent Rating",
    yaxis_title="Probability",
    height=400,
    showlegend=False
)

st.plotly_chart(dist_fig, use_container_width=True)

# Individual persona explorer
st.markdown("---")
st.markdown("## Individual Persona Explorer")

st.markdown("Explore detailed ratings for any persona:")

selected_persona_id = st.selectbox(
    "Select persona:",
    options=[p.persona_id for p in personas],
    format_func=lambda x: f"{x.upper()}: {next(p for p in personas if p.persona_id == x).age}yo {next(p for p in personas if p.persona_id == x).role}"
)

persona = next(p for p in personas if p.persona_id == selected_persona_id)
persona_data = df[df["persona_id"] == selected_persona_id]

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"""
    ### {selected_persona_id.upper()}

    **Age:** {persona.age}

    **Role:** {persona.role}

    **Visit Frequency:** {persona.visit_frequency}

    **Income:** {persona.income_level.value}

    **Location:** {persona.location}
    """)

with col2:
    # Create ratings chart
    persona_ratings = []
    persona_concepts = []

    for _, row in persona_data.iterrows():
        persona_concepts.append(concept_names[row["concept_id"]])
        persona_ratings.append(row["avg_mean_rating"])

    persona_fig = go.Figure(data=[
        go.Bar(
            y=persona_concepts,
            x=persona_ratings,
            orientation='h',
            marker_color=["#ff6b6b", "#4ecdc4", "#45b7d1"],
            text=[f"{r:.2f}" for r in persona_ratings],
            textposition="outside"
        )
    ])

    persona_fig.update_layout(
        title=f"{selected_persona_id.upper()} - Subscription Intent",
        xaxis_title="Rating (1-5)",
        xaxis_range=[0, 5],
        height=300,
        showlegend=False
    )
    persona_fig.add_vline(x=3.0, line_dash="dash", line_color="gray")

    st.plotly_chart(persona_fig, use_container_width=True)

    # Show sample response
    st.markdown("#### Sample Response")
    selected_concept_data = next((d for d in data if d["persona_id"] == selected_persona_id and d["concept_id"] == "c1"), None)
    if selected_concept_data and "sample_responses" in selected_concept_data:
        st.info(f'"{selected_concept_data["sample_responses"][0]}"')

st.markdown("---")
st.caption("Use interactive charts to explore subscription intent across different personas and session types →")
