# Forno SSR Analysis - Web Dashboard

Interactive dashboard for viewing Semantic Similarity Rating (SSR) analysis results.

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Launch dashboard
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## Dashboard Pages

### 🏠 Home
- Overview of SSR methodology
- Quick stats (14 personas, 3 concepts, $1.68 cost)
- Key finding callout (Shopify opportunity)

### 📊 Executive Summary
- Winner: Sandwich + Coffee Pass (3.35/5.0)
- Top 3 findings from expanded analysis
- Comparison: 14 personas vs original 8
- Two-track launch recommendations (B2B + B2C)
- Implementation timeline

### 👥 Personas
- 14 customer profiles with detailed descriptions
- Individual subscription intent ratings
- Filter by: All / Original 8 / New 6
- Session type classification
- Highlight: Top 3 personas (p11 Shopify, p1 Startup, p12 Condo)

### 📍 Demographics
- King Street market overview (30K residents, Shopify anchor)
- 3 acquisition channels (office, condo, transit)
- 7 session type framework
- Temporal patterns (weekday/weekend dynamics)
- Shopify proximity advantage analysis
- Income level vs subscription intent

### 📈 Results & Analysis
- Interactive persona × concept heatmap
- Top 5 personas per concept
- Session type analysis (temporal patterns)
- Probability distribution charts
- Individual persona explorer with sample responses

### 🎯 Recommendations
- Two-track strategy (B2B Shopify + B2C public)
- Detailed implementation plans
- Revenue projections ($5K Shopify, $6K B2C = $11K MRR)
- Additional subscription opportunities
- Implementation timeline with KPIs
- Risk mitigation strategies
- Success metrics & decision gates

## Features

### Interactive Visualizations
- All charts built with Plotly (hover, zoom, pan)
- Heatmaps, bar charts, line charts, pie charts
- Color-coded by performance (red/yellow/green)

### Data Exploration
- Filter personas by type
- Select concepts to view distributions
- Individual persona deep-dive
- Session type grouping

### Business-Focused
- Revenue projections
- KPIs and success metrics
- Risk mitigation
- Next action recommendations

## Data Source

Dashboard loads from latest aggregated results:
```
data/aggregated_results_YYYYMMDD_HHMMSS.json
```

If no data exists, run survey first:
```bash
python scripts/run_survey.py
```

## Dependencies

- streamlit>=1.31.0 - Web framework
- plotly>=5.18.0 - Interactive charts
- pandas>=2.2.0 - Data manipulation
- All other dependencies from requirements.txt

## Customization

### Add New Pages

Create file in `pages/` folder:
```
pages/N_📄_Page_Name.py
```

Streamlit auto-detects and adds to sidebar (alphabetical by N).

### Modify Existing Pages

Edit files in `pages/` folder:
- `1_📊_Executive_Summary.py`
- `2_👥_Personas.py`
- `3_📍_Demographics.py`
- `4_📈_Results.py`
- `5_🎯_Recommendations.py`

Changes reflect immediately (Streamlit auto-reloads).

## Deployment Options

### Local (Current)
```bash
streamlit run app.py
```

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repo
4. Deploy

### Docker
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Tips

- **Slow load?** Add `@st.cache_data` to expensive functions (already applied to data loading)
- **Port conflict?** Use `streamlit run app.py --server.port=8502`
- **Development mode?** Streamlit auto-reloads on file changes
- **Share locally?** Use `--server.address=0.0.0.0` to allow network access

## Screenshots

**Home Page:**
- Overview with quick stats
- Key finding callout

**Executive Summary:**
- Concept comparison chart
- Top 3 insights in columns
- Implementation timeline table

**Personas:**
- Expandable persona cards
- Individual rating charts
- Session type mapping

**Demographics:**
- Acquisition channel breakdown
- Temporal pattern visualization
- Proximity impact chart

**Results:**
- 14×3 interactive heatmap
- Session type grouped bar chart
- Individual persona explorer

**Recommendations:**
- Two-track strategy visualization
- Revenue projection charts
- Timeline table with KPIs

## Troubleshooting

**"No module named streamlit"**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**"No aggregated results found"**
```bash
python scripts/run_survey.py
```

**Port 8501 already in use**
```bash
streamlit run app.py --server.port=8502
```

**Can't import forno_ssr**
- Make sure you're in project root when running `streamlit run app.py`
- Paths use `Path(__file__).parent` to find src folder

## Next Steps

1. **Run locally** - Test all pages
2. **Customize** - Adjust colors, layouts, text
3. **Deploy** - Push to Streamlit Cloud for public access
4. **Share** - Send link to stakeholders for interactive exploration

---

**Last updated:** June 15, 2026
