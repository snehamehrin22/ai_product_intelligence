"""
Script 2: Calculate Closure Rates (Fixed for actual StatCan data structure)

Calculates closure rates over time for Toronto food services using the actual
long-form StatCan data structure.

Usage:
    python scripts/2_calculate_closure_rates_fixed.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from schemas import ClosureRateAnalysis

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_and_process_data() -> pd.DataFrame:
    """Load and pivot StatCan data into usable format."""
    print("📂 Loading business openings/closures data...")

    df = pd.read_csv(RAW_DIR / "business_openings_closures.csv")
    print(f"   Loaded {len(df):,} rows")

    # Filter for Toronto and Accommodation/food services
    df_filtered = df[
        (df['GEO'].str.contains('Toronto', case=False, na=False)) &
        (df['Industry'] == 'Accommodation and food services [72]')
    ].copy()

    print(f"   Filtered to Toronto food services: {len(df_filtered):,} rows")

    # Extract year from REF_DATE
    df_filtered['year'] = pd.to_datetime(df_filtered['REF_DATE']).dt.year

    # Pivot the data: rows = (year, month), columns = business dynamics measure
    df_pivot = df_filtered.pivot_table(
        index=['year', 'REF_DATE'],
        columns='Business dynamics measure',
        values='VALUE',
        aggfunc='first'
    ).reset_index()

    print(f"   Pivoted to {len(df_pivot)} month-year observations")
    print(f"   Columns available: {df_pivot.columns.tolist()}")

    return df_pivot

def calculate_annual_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate annual closure rates."""
    print("\n🔢 Calculating annual closure rates...")

    # Group by year and sum closures, average active businesses
    annual = df.groupby('year').agg({
        'Closing businesses': 'sum',
        'Active businesses': 'mean',
        'Opening businesses': 'sum',
        'Continuing businesses': 'mean'
    }).reset_index()

    # Calculate closure rate (annual closures ÷ average active establishments)
    annual['closure_rate'] = (annual['Closing businesses'] / annual['Active businesses']) * 100

    # Rename columns for clarity
    annual.columns = ['year', 'closures', 'active_establishments', 'openings', 'continuing', 'closure_rate']

    # Filter for complete years only (2015-2025, exclude partial 2026)
    annual = annual[annual['year'] <= 2025]

    print(f"   ✅ Calculated rates for {len(annual)} years")
    print(f"\n   Summary:")
    print(annual[['year', 'closures', 'active_establishments', 'closure_rate']].to_string(index=False))

    return annual

def detect_trend(df: pd.DataFrame) -> str:
    """Detect trend in closure rates."""
    from scipy import stats

    if len(df) < 3:
        return 'unclear'

    x = df['year'].values
    y = df['closure_rate'].values
    mask = ~np.isnan(y)

    if mask.sum() < 2:
        return 'unclear'

    slope, _, _, _, _ = stats.linregress(x[mask], y[mask])

    if abs(slope) < 0.5:
        return 'stable'
    elif slope > 0.5:
        return 'accelerating'
    else:
        return 'decelerating'

def visualize(df: pd.DataFrame, output_path: Path):
    """Create visualization."""
    print("\n📊 Creating visualization...")

    fig, ax = plt.subplots(figsize=(14, 7))

    # Line plot
    ax.plot(df['year'], df['closure_rate'],
            marker='o', linewidth=2.5, markersize=10, color='#e74c3c', label='Closure Rate')

    # Add trend line
    from scipy import stats
    x = df['year'].values
    y = df['closure_rate'].values
    mask = ~np.isnan(y)

    if mask.sum() > 1:
        slope, intercept, _, _, _ = stats.linregress(x[mask], y[mask])
        trend_line = slope * x + intercept
        ax.plot(x, trend_line, '--', color='#95a5a6', linewidth=2, alpha=0.7, label=f'Trend (slope={slope:.2f})')

    # Styling
    ax.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('Annual Closure Rate (%)', fontsize=13, fontweight='bold')
    ax.set_title('Toronto Accommodation & Food Services: Annual Closure Rate\n(Closures ÷ Active Establishments × 100)',
                 fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='best')

    # Add data labels
    for _, row in df.iterrows():
        ax.annotate(f"{row['closure_rate']:.1f}%",
                   xy=(row['year'], row['closure_rate']),
                   textcoords="offset points", xytext=(0,10),
                   ha='center', fontsize=9, color='#2c3e50')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_path}")

def main():
    print("=" * 70)
    print("TORONTO FOOD SERVICES: CLOSURE RATE ANALYSIS")
    print("=" * 70)

    # Load and process
    df_pivot = load_and_process_data()
    annual = calculate_annual_rates(df_pivot)

    # Save
    output_csv = PROCESSED_DIR / "closure_rates_by_year.csv"
    annual.to_csv(output_csv, index=False)
    print(f"\n💾 Saved to: {output_csv}")

    # Analyze
    trend = detect_trend(annual)
    peak_idx = annual['closure_rate'].idxmax()
    peak_year = int(annual.loc[peak_idx, 'year'])
    peak_rate = annual.loc[peak_idx, 'closure_rate']
    avg_rate = annual['closure_rate'].mean()
    total_closures = int(annual['closures'].sum())

    # Create analysis model
    analysis = ClosureRateAnalysis(
        category="Accommodation and Food Services (NAICS 72)",
        naics="72",
        time_period=f"{int(annual['year'].min())}-{int(annual['year'].max())}",
        total_closures=total_closures,
        average_annual_closure_rate=round(avg_rate, 2),
        peak_closure_year=str(peak_year),
        peak_closure_rate=round(peak_rate, 2),
        trend=trend,
        evidence=f"Analysis of {len(annual)} years. Rates range {annual['closure_rate'].min():.2f}% to {annual['closure_rate'].max():.2f}%."
    )

    # Print findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"✅ Time period: {analysis.time_period}")
    print(f"✅ Total closures: {analysis.total_closures:,}")
    print(f"✅ Average annual closure rate: {analysis.average_annual_closure_rate}%")
    print(f"✅ Peak year: {analysis.peak_closure_year} ({analysis.peak_closure_rate}%)")
    print(f"✅ Trend: {analysis.trend.upper()}")

    if analysis.trend == 'accelerating':
        print("\n⚠️  STRUCTURAL RESET CONFIRMED: Closure rates are ACCELERATING")
    elif analysis.trend == 'stable':
        print("\n✅ Closure rates are STABLE (steady-state churn)")
    else:
        print("\n✅ Closure rates are DECELERATING")

    # Visualize
    viz_path = PROCESSED_DIR / "closure_rate_visualization.png"
    visualize(annual, viz_path)

    print("\n" + "=" * 70)
    print("✅ Analysis complete! Run next script:")
    print("   python scripts/3_test_alcohol_hypothesis.py")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
