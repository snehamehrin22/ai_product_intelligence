"""
Script 2: Calculate Closure Rates

Calculates closure rates over time for Toronto food services:
- closure rate = closures ÷ active establishments
- Identifies trends (accelerating, stable, decelerating)
- Tests "structural reset" hypothesis

Requires:
- data/raw/business_openings_closures.csv (from script 1)
- data/raw/business_counts.csv (from script 1)

Outputs:
- data/processed/closure_rates_by_year.csv
- data/processed/closure_rate_visualization.png
- Console summary of findings

Usage:
    python scripts/2_calculate_closure_rates.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add parent directory to path for schemas import
sys.path.append(str(Path(__file__).parent.parent))
from schemas import ClosureRateAnalysis

# ============================================================================
# Configuration
# ============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Ensure output directory exists
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# ============================================================================
# Data Loading & Cleaning
# ============================================================================

def load_openings_closures() -> pd.DataFrame:
    """
    Load business openings/closures data and filter for Toronto food services.
    """
    print("📂 Loading business openings/closures data...")

    try:
        df = pd.read_csv(RAW_DIR / "business_openings_closures.csv")
        print(f"   Loaded {len(df):,} rows")

        # Display column names to help with filtering
        print(f"   Columns: {df.columns.tolist()}")

        # Filter for Toronto CMA (column name may vary)
        geo_cols = [col for col in df.columns if 'geo' in col.lower() or 'geography' in col.lower()]
        if geo_cols:
            geo_col = geo_cols[0]
            df_toronto = df[df[geo_col].str.contains('Toronto', case=False, na=False)]
            print(f"   Filtered to Toronto: {len(df_toronto):,} rows")
        else:
            print("   ⚠️  No geography column found, using all data")
            df_toronto = df

        # Filter for food services (NAICS 72 or 722)
        naics_cols = [col for col in df.columns if 'naics' in col.lower() or 'industry' in col.lower()]
        if naics_cols:
            naics_col = naics_cols[0]
            # Look for NAICS 72 or 722
            df_food = df_toronto[
                df_toronto[naics_col].str.contains('72|722', case=False, na=False)
            ]
            print(f"   Filtered to food services: {len(df_food):,} rows")
        else:
            print("   ⚠️  No NAICS column found, using all data")
            df_food = df_toronto

        return df_food

    except FileNotFoundError:
        print("   ❌ File not found. Please run script 1 first.")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        sys.exit(1)


def load_business_counts() -> pd.DataFrame:
    """
    Load Canadian Business Counts and filter for Toronto food services.
    """
    print("\n📂 Loading business counts data...")

    try:
        df = pd.read_csv(RAW_DIR / "business_counts.csv")
        print(f"   Loaded {len(df):,} rows")

        # Display column names
        print(f"   Columns: {df.columns.tolist()}")

        # Filter for Toronto
        geo_cols = [col for col in df.columns if 'geo' in col.lower() or 'geography' in col.lower()]
        if geo_cols:
            geo_col = geo_cols[0]
            df_toronto = df[df[geo_col].str.contains('Toronto', case=False, na=False)]
            print(f"   Filtered to Toronto: {len(df_toronto):,} rows")
        else:
            print("   ⚠️  No geography column found")
            df_toronto = df

        # Filter for food services
        naics_cols = [col for col in df.columns if 'naics' in col.lower() or 'industry' in col.lower()]
        if naics_cols:
            naics_col = naics_cols[0]
            df_food = df_toronto[
                df_toronto[naics_col].str.contains('72|722', case=False, na=False)
            ]
            print(f"   Filtered to food services: {len(df_food):,} rows")
        else:
            print("   ⚠️  No NAICS column found")
            df_food = df_toronto

        return df_food

    except FileNotFoundError:
        print("   ❌ File not found. Please run script 1 first.")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        sys.exit(1)


# ============================================================================
# Analysis Functions
# ============================================================================

def calculate_annual_closure_rates(openings_df: pd.DataFrame, counts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate annual closure rates: closures ÷ active establishments.

    Args:
        openings_df: Openings/closures data (monthly)
        counts_df: Business counts data (semi-annual)

    Returns:
        DataFrame with columns: year, closures, active_establishments, closure_rate
    """
    print("\n🔢 Calculating annual closure rates...")

    # Find date/period column in openings data
    date_cols = [col for col in openings_df.columns if 'date' in col.lower() or 'ref' in col.lower() or 'period' in col.lower()]
    if not date_cols:
        print("   ❌ No date column found in openings data")
        return pd.DataFrame()

    date_col = date_cols[0]
    print(f"   Using date column: {date_col}")

    # Convert to datetime and extract year
    try:
        openings_df['year'] = pd.to_datetime(openings_df[date_col]).dt.year
    except:
        # Try extracting year directly if format is YYYY or YYYY-MM
        openings_df['year'] = openings_df[date_col].astype(str).str[:4].astype(int)

    # Find closures column
    closure_cols = [col for col in openings_df.columns if 'closure' in col.lower() or 'closing' in col.lower()]
    if not closure_cols:
        print("   ❌ No closures column found")
        return pd.DataFrame()

    closure_col = closure_cols[0]
    print(f"   Using closures column: {closure_col}")

    # Aggregate closures by year
    annual_closures = openings_df.groupby('year')[closure_col].sum().reset_index()
    annual_closures.columns = ['year', 'closures']
    print(f"   Calculated closures for {len(annual_closures)} years")

    # Find establishment count column in counts data
    count_cols = [col for col in counts_df.columns if 'establishment' in col.lower() or 'count' in col.lower() or 'value' in col.lower()]
    if not count_cols:
        print("   ⚠️  No establishment count column found, using estimate")
        # Use average of "continuing" businesses from openings data as estimate
        continuing_cols = [col for col in openings_df.columns if 'continu' in col.lower()]
        if continuing_cols:
            avg_establishments = int(openings_df[continuing_cols[0]].mean())
            annual_closures['active_establishments'] = avg_establishments
        else:
            print("   ❌ Cannot estimate active establishments")
            return pd.DataFrame()
    else:
        count_col = count_cols[0]
        # Get most recent business count for each year
        date_cols_counts = [col for col in counts_df.columns if 'date' in col.lower() or 'ref' in col.lower()]
        if date_cols_counts:
            try:
                counts_df['year'] = pd.to_datetime(counts_df[date_cols_counts[0]]).dt.year
            except:
                counts_df['year'] = counts_df[date_cols_counts[0]].astype(str).str[:4].astype(int)

            annual_counts = counts_df.groupby('year')[count_col].mean().reset_index()
            annual_counts.columns = ['year', 'active_establishments']

            # Merge with closures
            annual_closures = annual_closures.merge(annual_counts, on='year', how='left')

    # Calculate closure rate
    annual_closures['closure_rate'] = (annual_closures['closures'] / annual_closures['active_establishments']) * 100

    # Sort by year
    annual_closures = annual_closures.sort_values('year')

    print(f"   ✅ Calculated closure rates for {len(annual_closures)} years")

    return annual_closures


def detect_trend(closure_rates_df: pd.DataFrame) -> str:
    """
    Detect if closure rate is accelerating, stable, or decelerating.

    Args:
        closure_rates_df: DataFrame with 'year' and 'closure_rate' columns

    Returns:
        'accelerating', 'stable', or 'decelerating'
    """
    if len(closure_rates_df) < 3:
        return 'unclear'

    # Fit linear regression
    from scipy import stats
    x = closure_rates_df['year'].values
    y = closure_rates_df['closure_rate'].values

    # Remove any NaN values
    mask = ~np.isnan(y)
    x = x[mask]
    y = y[mask]

    if len(x) < 2:
        return 'unclear'

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Interpret slope
    if abs(slope) < 0.1:
        return 'stable'
    elif slope > 0.1:
        return 'accelerating'
    else:
        return 'decelerating'


def visualize_closure_rates(closure_rates_df: pd.DataFrame, output_path: Path):
    """
    Create visualization of closure rates over time.
    """
    print("\n📊 Creating visualization...")

    fig, ax = plt.subplots(figsize=(12, 6))

    # Line plot
    ax.plot(closure_rates_df['year'], closure_rates_df['closure_rate'],
            marker='o', linewidth=2, markersize=8, color='#e74c3c')

    # Add trend line
    from scipy import stats
    x = closure_rates_df['year'].values
    y = closure_rates_df['closure_rate'].values
    mask = ~np.isnan(y)
    if mask.sum() > 1:
        slope, intercept, _, _, _ = stats.linregress(x[mask], y[mask])
        trend_line = slope * x + intercept
        ax.plot(x, trend_line, '--', color='#95a5a6', alpha=0.7, label='Trend')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Closure Rate (%)', fontsize=12)
    ax.set_title('Toronto Food Services: Annual Closure Rate (2015-2026)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved visualization to: {output_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    """
    Main function to calculate closure rates and generate outputs.
    """
    print("=" * 70)
    print("CLOSURE RATE ANALYSIS")
    print("=" * 70)

    # Load data
    openings_df = load_openings_closures()
    counts_df = load_business_counts()

    # Calculate closure rates
    closure_rates_df = calculate_annual_closure_rates(openings_df, counts_df)

    if closure_rates_df.empty:
        print("\n❌ Failed to calculate closure rates. Check data quality.")
        return

    # Save processed data
    output_csv = PROCESSED_DIR / "closure_rates_by_year.csv"
    closure_rates_df.to_csv(output_csv, index=False)
    print(f"\n💾 Saved closure rates to: {output_csv}")

    # Detect trend
    trend = detect_trend(closure_rates_df)

    # Find peak year
    peak_year = closure_rates_df.loc[closure_rates_df['closure_rate'].idxmax(), 'year']
    peak_rate = closure_rates_df['closure_rate'].max()

    # Calculate average
    avg_rate = closure_rates_df['closure_rate'].mean()

    # Create ClosureRateAnalysis model
    analysis = ClosureRateAnalysis(
        category="All Food Services (NAICS 722)",
        naics="722",
        time_period=f"{closure_rates_df['year'].min()}-{closure_rates_df['year'].max()}",
        total_closures=int(closure_rates_df['closures'].sum()),
        average_annual_closure_rate=round(avg_rate, 2),
        peak_closure_year=str(int(peak_year)),
        peak_closure_rate=round(peak_rate, 2),
        trend=trend,
        evidence=f"Closure rates range from {closure_rates_df['closure_rate'].min():.2f}% to {closure_rates_df['closure_rate'].max():.2f}%. Trend is {trend}."
    )

    # Print summary
    print("\n" + "=" * 70)
    print("FINDINGS SUMMARY")
    print("=" * 70)
    print(f"\n✅ Structural Reset Assessment")
    print(f"   Time period: {analysis.time_period}")
    print(f"   Total closures: {analysis.total_closures:,}")
    print(f"   Average closure rate: {analysis.average_annual_closure_rate}% per year")
    print(f"   Peak year: {analysis.peak_closure_year} ({analysis.peak_closure_rate}%)")
    print(f"   Trend: {analysis.trend.upper()}")

    # Visualize
    viz_path = PROCESSED_DIR / "closure_rate_visualization.png"
    visualize_closure_rates(closure_rates_df, viz_path)

    # Next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("✅ Closure rate analysis complete!")
    print("\nRun next script:")
    print("   python scripts/3_test_alcohol_hypothesis.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
