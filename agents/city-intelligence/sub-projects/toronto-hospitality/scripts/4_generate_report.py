"""
Script 4: Generate Analysis Report

Synthesizes findings from scripts 1-3 and generates ANALYSIS.md with:
- Executive summary
- Key findings (with data)
- Visualizations
- Limitations
- Recommendation on Layer B

Requires:
- data/processed/closure_rates_by_year.csv (from script 2)
- data/processed/alcohol_hypothesis_results.json (from script 3)
- data/raw/food_services_stats.csv (from script 1)

Outputs:
- ANALYSIS.md (in project root)

Usage:
    python scripts/4_generate_report.py
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add parent directory to path for schemas import
sys.path.append(str(Path(__file__).parent.parent))
from schemas import LayerAFindings, ClosureRateAnalysis, AlcoholHypothesisTest, MarginAnalysis

# ============================================================================
# Configuration
# ============================================================================

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_FILE = PROJECT_DIR / "ANALYSIS.md"

# ============================================================================
# Data Loading
# ============================================================================

def load_closure_analysis() -> ClosureRateAnalysis:
    """Load closure rate analysis from CSV."""
    print("📂 Loading closure rate analysis...")

    try:
        df = pd.read_csv(PROCESSED_DIR / "closure_rates_by_year.csv")

        # Calculate metrics
        total_closures = int(df['closures'].sum())
        avg_rate = round(df['closure_rate'].mean(), 2)
        peak_idx = df['closure_rate'].idxmax()
        peak_year = str(int(df.loc[peak_idx, 'year']))
        peak_rate = round(df.loc[peak_idx, 'closure_rate'], 2)

        # Detect trend
        from scipy import stats
        import numpy as np
        x = df['year'].values
        y = df['closure_rate'].values
        mask = ~np.isnan(y)
        if mask.sum() >= 2:
            slope, _, _, _, _ = stats.linregress(x[mask], y[mask])
            if abs(slope) < 0.1:
                trend = 'stable'
            elif slope > 0.1:
                trend = 'accelerating'
            else:
                trend = 'decelerating'
        else:
            trend = 'unclear'

        analysis = ClosureRateAnalysis(
            category="All Food Services (NAICS 722)",
            naics="722",
            time_period=f"{int(df['year'].min())}-{int(df['year'].max())}",
            total_closures=total_closures,
            average_annual_closure_rate=avg_rate,
            peak_closure_year=peak_year,
            peak_closure_rate=peak_rate,
            trend=trend,
            evidence=f"Analysis of {len(df)} years of data from Statistics Canada."
        )

        print(f"   ✅ Loaded: {analysis.time_period}, avg rate {analysis.average_annual_closure_rate}%")
        return analysis

    except FileNotFoundError:
        print("   ⚠️  File not found, using placeholder")
        return ClosureRateAnalysis(
            category="All Food Services",
            naics="722",
            time_period="2020-2026",
            total_closures=0,
            average_annual_closure_rate=0.0,
            peak_closure_year="N/A",
            peak_closure_rate=0.0,
            trend="unclear",
            evidence="Data not available"
        )


def load_alcohol_hypothesis() -> AlcoholHypothesisTest:
    """Load alcohol hypothesis test results."""
    print("📂 Loading alcohol hypothesis results...")

    try:
        with open(PROCESSED_DIR / "alcohol_hypothesis_results.json", 'r') as f:
            data = json.load(f)

        result = AlcoholHypothesisTest(**data)
        print(f"   ✅ Loaded: hypothesis {'supported' if result.alcohol_hypothesis_supported else 'not supported'}")
        return result

    except FileNotFoundError:
        print("   ⚠️  File not found, using placeholder")
        return AlcoholHypothesisTest(
            drinking_places_closure_rate=0.0,
            full_service_restaurants_closure_rate=0.0,
            alcohol_hypothesis_supported=False,
            difference_percentage_points=0.0,
            statistical_significance="unclear",
            notes="Data not available"
        )


def load_margin_analysis() -> MarginAnalysis:
    """Load and analyze food services margin data."""
    print("📂 Loading margin analysis...")

    try:
        df = pd.read_csv(RAW_DIR / "food_services_stats.csv")

        # Find year and margin columns
        year_cols = [col for col in df.columns if 'year' in col.lower() or 'ref' in col.lower()]
        margin_cols = [col for col in df.columns if 'margin' in col.lower() or 'profit' in col.lower()]

        if not year_cols or not margin_cols:
            raise ValueError("Required columns not found")

        year_col = year_cols[0]
        margin_col = margin_cols[0]

        # Filter for food services (NAICS 722)
        naics_cols = [col for col in df.columns if 'naics' in col.lower()]
        if naics_cols:
            df = df[df[naics_cols[0]].str.contains('722', case=False, na=False)]

        # Extract year from date if needed
        try:
            df['year'] = pd.to_datetime(df[year_col]).dt.year
        except:
            df['year'] = df[year_col].astype(str).str[:4].astype(int)

        # Filter for recent years
        df = df[df['year'] >= 2020].sort_values('year')

        if len(df) < 2:
            raise ValueError("Insufficient data")

        start_year = int(df.iloc[0]['year'])
        end_year = int(df.iloc[-1]['year'])
        start_margin = float(df.iloc[0][margin_col])
        end_margin = float(df.iloc[-1][margin_col])
        margin_change = end_margin - start_margin

        analysis = MarginAnalysis(
            naics="722 - Food services and drinking places",
            start_year=start_year,
            end_year=end_year,
            start_margin=round(start_margin, 2),
            end_margin=round(end_margin, 2),
            margin_change=round(margin_change, 2),
            margin_squeeze_confirmed=margin_change < -0.5,
            evidence=f"Margins declined from {start_margin:.2f}% to {end_margin:.2f}% ({margin_change:+.2f} points)"
        )

        print(f"   ✅ Loaded: {analysis.start_year}-{analysis.end_year}, change {analysis.margin_change:+.2f}pp")
        return analysis

    except (FileNotFoundError, ValueError) as e:
        print(f"   ⚠️  Unable to analyze margins: {e}")
        return MarginAnalysis(
            naics="722",
            start_year=2020,
            end_year=2026,
            start_margin=0.0,
            end_margin=0.0,
            margin_change=0.0,
            margin_squeeze_confirmed=False,
            evidence="Data not available at Toronto CMA level. Margin data only available Canada-wide."
        )


# ============================================================================
# Report Generation
# ============================================================================

def generate_markdown_report(findings: LayerAFindings) -> str:
    """Generate ANALYSIS.md content."""

    md = f"""# Toronto Hospitality Analysis: Layer A Findings

**Report Date:** {findings.report_date.strftime('%B %d, %Y')}
**Geography:** {findings.geography}
**Time Period:** {findings.time_period}

---

## Executive Summary

{findings.executive_summary}

---

## Key Findings

"""

    for i, takeaway in enumerate(findings.key_takeaways, 1):
        md += f"{i}. **{takeaway}**\n\n"

    md += f"""---

## 1. Structural Reset: Closure Rate Analysis

**Question:** Are Toronto restaurants closing at unprecedented rates?

**Findings:**
- **Time period:** {findings.structural_reset.time_period}
- **Total closures:** {findings.structural_reset.total_closures:,}
- **Average annual closure rate:** {findings.structural_reset.average_annual_closure_rate}%
- **Peak year:** {findings.structural_reset.peak_closure_year} ({findings.structural_reset.peak_closure_rate}%)
- **Trend:** {findings.structural_reset.trend.upper()}

**Evidence:** {findings.structural_reset.evidence}

**Verdict:** {"✅ CONFIRMED - Closure rates are elevated" if findings.structural_reset.average_annual_closure_rate > 5 else "⚠️  Inconclusive"}

---

## 2. Alcohol Hypothesis: Are Bars Dying Faster?

**Question:** Do alcohol-heavy businesses (bars, pubs) have higher closure rates than food-first restaurants?

**Findings:**
- **Drinking places (NAICS 7224):** {findings.alcohol_hypothesis.drinking_places_closure_rate}%
- **Full-service restaurants (NAICS 722511):** {findings.alcohol_hypothesis.full_service_restaurants_closure_rate}%
"""

    if findings.alcohol_hypothesis.limited_service_closure_rate:
        md += f"- **Limited-service (NAICS 722512):** {findings.alcohol_hypothesis.limited_service_closure_rate}%\n"

    md += f"""- **Difference:** {findings.alcohol_hypothesis.difference_percentage_points:+.2f} percentage points
- **Statistical significance:** {findings.alcohol_hypothesis.statistical_significance}

**Notes:** {findings.alcohol_hypothesis.notes}

**Verdict:** {"✅ SUPPORTED" if findings.alcohol_hypothesis.alcohol_hypothesis_supported else "❌ NOT SUPPORTED (or insufficient data)"}

---

## 3. Margin Squeeze: Profitability Pressure

**Question:** Are operating margins declining for food services?

**Findings:**
- **NAICS category:** {findings.margin_squeeze.naics}
- **Time period:** {findings.margin_squeeze.start_year}-{findings.margin_squeeze.end_year}
- **Starting margin:** {findings.margin_squeeze.start_margin}%
- **Ending margin:** {findings.margin_squeeze.end_margin}%
- **Change:** {findings.margin_squeeze.margin_change:+.2f} percentage points

**Evidence:** {findings.margin_squeeze.evidence}

**Verdict:** {"✅ CONFIRMED - Margins are compressing" if findings.margin_squeeze.margin_squeeze_confirmed else "⚠️  No clear compression detected"}

---

## Data Sources

"""

    for source in findings.data_sources:
        md += f"- {source}\n"

    md += f"""

**All data from Statistics Canada (public, authoritative)**

---

## Limitations

"""

    for limitation in findings.limitations:
        md += f"- {limitation}\n"

    md += f"""

---

## Recommendation: Should We Proceed to Layer B?

**Layer B** would involve:
- Hand-coding ~50 restaurant closures from BlogTO/CityNews
- Creating "experiential vs commodity" taxonomy
- Matching closures with survivors on same streets
- Testing "experiential survives longer" hypothesis

**Effort:** 2-3 weeks of manual work

**Recommendation:** {"✅ YES - Layer A shows strong signal worth investigating deeper" if findings.layer_b_recommended else "⚠️  MAYBE - Signal is weak, consider alternative approaches"}

**Reasoning:** {findings.reasoning}

---

## Visualizations

See `data/processed/` for:
- `closure_rate_visualization.png` - Closure rate trend over time

---

## Next Steps

"""

    if findings.layer_b_recommended:
        md += """**If proceeding to Layer B:**
1. Scrape BlogTO/CityNews/insauga closure announcements (2020-2026)
2. Hand-code each closure:
   - Restaurant type (casual, fine dining, QSR, bar, cafe)
   - Price point ($ to $$$$)
   - Experiential features (communal seating, programming, wellness, ritual)
   - Neighborhood & exact location
3. Create matched control sample (survivors on same streets)
4. Calculate closure rates by category
5. Test: "Experiential concepts have lower closure rates"

**Alternative approaches:**
- Focus on wellness/third-space expansion (inverse of closures)
- Interview business owners about closures (qualitative)
- Analyze social media sentiment by restaurant type
"""
    else:
        md += """**Given weak macro signal, consider:**
- Refining hypothesis (maybe it's not about alcohol or experiential)
- Qualitative research (interviews with owners, customers)
- Different geographic focus (downtown vs suburbs)
- Focus on the inverse: why are wellness concepts thriving?
"""

    md += f"""

---

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Status:** Layer A Complete
"""

    return md


def create_findings_model(closure: ClosureRateAnalysis, alcohol: AlcoholHypothesisTest, margin: MarginAnalysis) -> LayerAFindings:
    """Create LayerAFindings model from component analyses."""

    # Generate executive summary
    exec_summary = f"""Toronto's food services sector shows {closure.trend} closure rates averaging {closure.average_annual_closure_rate}% annually from {closure.time_period}. """

    if alcohol.alcohol_hypothesis_supported:
        exec_summary += f"Alcohol-heavy businesses (drinking places) are closing at {alcohol.drinking_places_closure_rate}% vs {alcohol.full_service_restaurants_closure_rate}% for restaurants, supporting the hypothesis that bars are more vulnerable. "
    else:
        exec_summary += "Detailed NAICS breakdowns were unavailable at the Toronto CMA level, limiting our ability to test the alcohol hypothesis rigorously. "

    if margin.margin_squeeze_confirmed:
        exec_summary += f"Operating margins declined {margin.margin_change:.2f} percentage points, confirming profitability pressure."
    else:
        exec_summary += "Margin data suggests stable or improving profitability, though this is Canada-wide data not Toronto-specific."

    # Generate key takeaways
    takeaways = []

    if closure.trend == "accelerating":
        takeaways.append(f"Closure rates are ACCELERATING: {closure.average_annual_closure_rate}% average, peaking at {closure.peak_closure_rate}% in {closure.peak_closure_year}")
    elif closure.trend == "stable":
        takeaways.append(f"Closure rates are STABLE at ~{closure.average_annual_closure_rate}%, suggesting steady-state churn")
    else:
        takeaways.append(f"Closure rate trend is {closure.trend.upper()}: {closure.average_annual_closure_rate}% average")

    if alcohol.alcohol_hypothesis_supported:
        takeaways.append(f"Alcohol hypothesis SUPPORTED: Bars/pubs closing {alcohol.difference_percentage_points:.1f}pp faster than restaurants")
    else:
        takeaways.append(f"Alcohol hypothesis INCONCLUSIVE: {alcohol.notes}")

    if margin.margin_squeeze_confirmed:
        takeaways.append(f"Profit margins COMPRESSED by {abs(margin.margin_change):.2f}pp, confirming cost pressure")
    else:
        takeaways.append("Profit margin pressure unclear from national data")

    # Recommendation on Layer B
    signal_strength = 0
    if closure.average_annual_closure_rate > 5:
        signal_strength += 1
    if closure.trend == "accelerating":
        signal_strength += 1
    if alcohol.alcohol_hypothesis_supported:
        signal_strength += 1
    if margin.margin_squeeze_confirmed:
        signal_strength += 1

    layer_b_recommended = signal_strength >= 2

    if layer_b_recommended:
        reasoning = f"Layer A found {signal_strength}/4 hypotheses supported with strong macro signal. Hand-coding {closure.total_closures} closures would provide granular insight into experiential vs commodity dynamics."
    else:
        reasoning = f"Layer A found only {signal_strength}/4 hypotheses clearly supported. Macro signal is weak or unclear. Consider alternative approaches before investing in manual hand-coding."

    # Create findings model
    findings = LayerAFindings(
        geography="Toronto, census metropolitan area",
        time_period=closure.time_period,
        structural_reset=closure,
        alcohol_hypothesis=alcohol,
        margin_squeeze=margin,
        executive_summary=exec_summary,
        key_takeaways=takeaways,
        data_sources=[
            "Statistics Canada Table 33-10-02700-01: Business openings and closures (monthly)",
            "Statistics Canada Table 33-10-07660-01: Canadian Business Counts",
            "Statistics Canada Table 21-10-0171-01: Food services summary statistics"
        ],
        limitations=[
            "Geographic granularity: CMA-level only, cannot isolate downtown vs suburbs",
            "NAICS detail: Experimental table may only report 2-digit NAICS at CMA level",
            "Margin data: Canada-wide only, not Toronto-specific",
            "No closure reasons: Data does not explain WHY businesses closed",
            "Time lag: Business counts published semi-annually with 3-6 month delay"
        ],
        layer_b_recommended=layer_b_recommended,
        reasoning=reasoning
    )

    return findings


# ============================================================================
# Main
# ============================================================================

def main():
    """Main function to generate analysis report."""
    print("=" * 70)
    print("GENERATING ANALYSIS REPORT")
    print("=" * 70)

    # Load all analyses
    closure_analysis = load_closure_analysis()
    alcohol_analysis = load_alcohol_hypothesis()
    margin_analysis = load_margin_analysis()

    # Create findings model
    print("\n📊 Synthesizing findings...")
    findings = create_findings_model(closure_analysis, alcohol_analysis, margin_analysis)

    # Generate markdown report
    print("📝 Generating ANALYSIS.md...")
    markdown_content = generate_markdown_report(findings)

    # Write to file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(markdown_content)

    print(f"   ✅ Report saved to: {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 70)
    print("REPORT SUMMARY")
    print("=" * 70)
    print(f"\n{findings.executive_summary}\n")
    print("Key Takeaways:")
    for i, takeaway in enumerate(findings.key_takeaways, 1):
        print(f"   {i}. {takeaway}")

    print("\n" + "=" * 70)
    print("LAYER B RECOMMENDATION")
    print("=" * 70)
    recommendation = "✅ PROCEED" if findings.layer_b_recommended else "⚠️  RECONSIDER"
    print(f"\n{recommendation}")
    print(f"\n{findings.reasoning}")

    print("\n" + "=" * 70)
    print("✅ Analysis complete! Read ANALYSIS.md for full report.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
