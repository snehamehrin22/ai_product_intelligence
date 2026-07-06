"""
Script 3: Test Alcohol Hypothesis

Tests whether alcohol-heavy businesses (drinking places) are failing at higher
rates than food-first restaurants.

Hypothesis: NAICS 7224 (drinking places) should have higher closure rates
than NAICS 722511 (full-service restaurants) and 722512 (limited-service).

Requires:
- data/raw/business_openings_closures.csv
- data/raw/business_counts.csv

Outputs:
- data/processed/alcohol_hypothesis_results.json
- Console summary of findings

Usage:
    python scripts/3_test_alcohol_hypothesis.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Add parent directory to path for schemas import
sys.path.append(str(Path(__file__).parent.parent))
from schemas import AlcoholHypothesisTest

# ============================================================================
# Configuration
# ============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# NAICS categories to compare
NAICS_CATEGORIES = {
    "7224": "Drinking places (alcoholic beverages)",
    "722511": "Full-service restaurants",
    "722512": "Limited-service eating places"
}

# ============================================================================
# Analysis Functions
# ============================================================================

def load_and_filter_data(naics_code: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load openings/closures and business counts data for a specific NAICS code.

    Args:
        naics_code: NAICS code to filter (e.g., "7224")

    Returns:
        Tuple of (openings_df, counts_df) filtered for the NAICS code
    """
    print(f"\n📂 Loading data for NAICS {naics_code} ({NAICS_CATEGORIES.get(naics_code, 'Unknown')})")

    try:
        # Load openings/closures
        openings_df = pd.read_csv(RAW_DIR / "business_openings_closures.csv")

        # Load business counts
        counts_df = pd.read_csv(RAW_DIR / "business_counts.csv")

        # Filter for Toronto
        for df in [openings_df, counts_df]:
            geo_cols = [col for col in df.columns if 'geo' in col.lower()]
            if geo_cols:
                mask = df[geo_cols[0]].str.contains('Toronto', case=False, na=False)
                df = df[mask]

        # Filter for specific NAICS code
        naics_cols_openings = [col for col in openings_df.columns if 'naics' in col.lower() or 'industry' in col.lower()]
        naics_cols_counts = [col for col in counts_df.columns if 'naics' in col.lower() or 'industry' in col.lower()]

        if naics_cols_openings:
            openings_filtered = openings_df[
                openings_df[naics_cols_openings[0]].str.contains(naics_code, case=False, na=False)
            ]
        else:
            print(f"   ⚠️  Cannot filter by NAICS code (no NAICS column found)")
            openings_filtered = openings_df

        if naics_cols_counts:
            counts_filtered = counts_df[
                counts_df[naics_cols_counts[0]].str.contains(naics_code, case=False, na=False)
            ]
        else:
            counts_filtered = counts_df

        print(f"   Found {len(openings_filtered)} closure records and {len(counts_filtered)} count records")

        return openings_filtered, counts_filtered

    except FileNotFoundError as e:
        print(f"   ❌ File not found: {e}")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return pd.DataFrame(), pd.DataFrame()


def calculate_closure_rate_for_naics(openings_df: pd.DataFrame, counts_df: pd.DataFrame) -> float:
    """
    Calculate average closure rate for a given NAICS category.

    Args:
        openings_df: Openings/closures data
        counts_df: Business counts data

    Returns:
        Average annual closure rate (%) or None if cannot calculate
    """
    if openings_df.empty or counts_df.empty:
        return None

    # Find closures column
    closure_cols = [col for col in openings_df.columns if 'closure' in col.lower()]
    if not closure_cols:
        print("   ⚠️  No closures column found")
        return None

    closure_col = closure_cols[0]

    # Find date column
    date_cols = [col for col in openings_df.columns if 'date' in col.lower() or 'ref' in col.lower() or 'period' in col.lower()]
    if date_cols:
        try:
            openings_df['year'] = pd.to_datetime(openings_df[date_cols[0]]).dt.year
        except:
            openings_df['year'] = openings_df[date_cols[0]].astype(str).str[:4].astype(int)

        # Filter for recent years (2020-2026)
        openings_df = openings_df[openings_df['year'] >= 2020]

    # Calculate total closures
    total_closures = openings_df[closure_col].sum()

    # Get average establishment count
    count_cols = [col for col in counts_df.columns if 'establishment' in col.lower() or 'count' in col.lower() or 'value' in col.lower()]
    if not count_cols:
        # Estimate from "continuing" businesses in openings data
        continuing_cols = [col for col in openings_df.columns if 'continu' in col.lower()]
        if continuing_cols:
            avg_establishments = openings_df[continuing_cols[0]].mean()
        else:
            print("   ⚠️  Cannot estimate active establishments")
            return None
    else:
        avg_establishments = counts_df[count_cols[0]].mean()

    if avg_establishments == 0 or pd.isna(avg_establishments):
        return None

    # Calculate annual closure rate
    num_years = openings_df['year'].nunique() if 'year' in openings_df.columns else 1
    annual_closures = total_closures / num_years
    closure_rate = (annual_closures / avg_establishments) * 100

    return round(closure_rate, 2)


def compare_categories() -> AlcoholHypothesisTest:
    """
    Compare closure rates across NAICS categories to test alcohol hypothesis.

    Returns:
        AlcoholHypothesisTest model with results
    """
    print("\n" + "=" * 70)
    print("TESTING ALCOHOL HYPOTHESIS")
    print("=" * 70)
    print("\nHypothesis: Drinking places (NAICS 7224) have higher closure rates")
    print("than food-first restaurants (NAICS 722511, 722512)")

    # Calculate closure rates for each category
    closure_rates = {}

    for naics_code, description in NAICS_CATEGORIES.items():
        openings_df, counts_df = load_and_filter_data(naics_code)
        rate = calculate_closure_rate_for_naics(openings_df, counts_df)
        closure_rates[naics_code] = rate

        if rate is not None:
            print(f"\n✅ {description}: {rate}% closure rate")
        else:
            print(f"\n⚠️  {description}: Unable to calculate")

    # Extract rates
    drinking_places_rate = closure_rates.get("7224")
    full_service_rate = closure_rates.get("722511")
    limited_service_rate = closure_rates.get("722512")

    # Determine if hypothesis is supported
    hypothesis_supported = False
    difference = 0.0
    significance = "unclear"
    notes = ""

    if drinking_places_rate is not None and full_service_rate is not None:
        difference = drinking_places_rate - full_service_rate

        if drinking_places_rate > full_service_rate:
            hypothesis_supported = True
            significance = "high" if abs(difference) > 2.0 else "medium"
            notes = f"Drinking places have {difference:.2f} percentage point higher closure rate than full-service restaurants."
        else:
            hypothesis_supported = False
            significance = "high"
            notes = f"Drinking places actually have {abs(difference):.2f} percentage point LOWER closure rate than full-service restaurants. Hypothesis NOT supported."
    else:
        notes = "Unable to test hypothesis due to insufficient data granularity. StatCan may not provide detailed NAICS breakdowns at CMA level."

    # Create result model
    result = AlcoholHypothesisTest(
        drinking_places_closure_rate=drinking_places_rate if drinking_places_rate is not None else 0.0,
        full_service_restaurants_closure_rate=full_service_rate if full_service_rate is not None else 0.0,
        limited_service_closure_rate=limited_service_rate,
        alcohol_hypothesis_supported=hypothesis_supported,
        difference_percentage_points=round(difference, 2),
        statistical_significance=significance,
        notes=notes
    )

    return result


# ============================================================================
# Main
# ============================================================================

def main():
    """
    Main function to test alcohol hypothesis.
    """
    print("=" * 70)
    print("ALCOHOL HYPOTHESIS TEST")
    print("=" * 70)

    # Run comparison
    result = compare_categories()

    # Print findings
    print("\n" + "=" * 70)
    print("FINDINGS SUMMARY")
    print("=" * 70)

    if result.notes.startswith("Unable"):
        print("\n⚠️  DATA LIMITATION")
        print(f"   {result.notes}")
        print("\n   Alternative approach:")
        print("   - Use national-level data (Canada-wide) for NAICS detail")
        print("   - Or proceed to Layer B with hand-coded closures")
    else:
        verdict = "✅ SUPPORTED" if result.alcohol_hypothesis_supported else "❌ NOT SUPPORTED"
        print(f"\n{verdict}")
        print(f"   Drinking places: {result.drinking_places_closure_rate}%")
        print(f"   Full-service restaurants: {result.full_service_restaurants_closure_rate}%")
        if result.limited_service_closure_rate:
            print(f"   Limited-service: {result.limited_service_closure_rate}%")
        print(f"   Difference: {result.difference_percentage_points} percentage points")
        print(f"   Significance: {result.statistical_significance}")
        print(f"\n   {result.notes}")

    # Save results
    output_file = PROCESSED_DIR / "alcohol_hypothesis_results.json"
    with open(output_file, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    # Next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("✅ Alcohol hypothesis test complete!")
    print("\nRun final script:")
    print("   python scripts/4_generate_report.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
