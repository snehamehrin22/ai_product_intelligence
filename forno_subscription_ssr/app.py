"""
Forno Cultura Subscription SSR Analysis - Web Dashboard

Interactive dashboard displaying Semantic Similarity Rating (SSR) analysis
for Forno King Street subscription concepts.
"""

import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Forno SSR Analysis",
    page_icon="🥖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .insight-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main page
st.markdown('<div class="main-header">🥖 Forno King Street Subscription Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Semantic Similarity Rating (SSR) Study - June 2026</div>', unsafe_allow_html=True)

# Introduction
st.markdown("""
## Welcome

This interactive dashboard presents the results of a **Semantic Similarity Rating (SSR)** study
conducted to predict customer subscription intent for Forno Cultura's King Street location.

### What is SSR?

SSR is a novel methodology developed by Maier et al. (2025) that:
- Uses AI to generate synthetic consumer responses
- Maps free-text responses to Likert scale ratings via semantic similarity
- Predicts purchase intent without expensive surveys

### Study Overview

**14 personas** × **3 subscription concepts** × **2 samples** = **84 survey responses**

**Total research cost:** $1.68 in API calls

---

Navigate using the sidebar to explore:
- **Executive Summary** - Top-line findings
- **Personas** - 14 customer types tested
- **Demographics** - King Street market analysis
- **Results** - Detailed findings and visualizations
- **Recommendations** - Actionable next steps
""")

# Quick stats in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Personas Tested",
        value="14",
        delta="6 new personas added"
    )

with col2:
    st.metric(
        label="Concepts Evaluated",
        value="3",
        delta="Subscription models"
    )

with col3:
    st.metric(
        label="Winning Concept",
        value="Sandwich + Coffee Pass",
        delta="3.35/5.0 rating"
    )

with col4:
    st.metric(
        label="Research Cost",
        value="$1.68",
        delta="vs $5K+ traditional survey"
    )

# Key insight callout
st.markdown("""
---

### 💡 Key Finding

The **Shopify worker persona** (next door at King-Portland Centre) showed the **highest subscription intent
of all 14 personas** (3.84/5.0), revealing a B2B corporate partnership opportunity worth $5,000/month
in recurring revenue.

This insight would have been missed with the original 8 personas.

---

**Navigation:** Use the sidebar to explore detailed analysis →
""")

# Footer
st.markdown("""
<div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #ddd; color: #666; font-size: 0.9rem;">
    <strong>Method:</strong> Semantic Similarity Rating (Maier et al., 2025)<br>
    <strong>Date:</strong> June 15, 2026<br>
    <strong>Location:</strong> Forno Cultura King Street (King & Portland, Toronto)
</div>
""", unsafe_allow_html=True)
