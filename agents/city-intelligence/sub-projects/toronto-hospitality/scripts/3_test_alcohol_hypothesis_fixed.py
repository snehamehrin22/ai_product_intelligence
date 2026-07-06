"""
Script 3: Test Alcohol Hypothesis (Fixed)

Tests whether drinking places (bars/pubs) have higher closure rates than restaurants.

Uses the "Food and beverage services (tourism)" category which breaks down into:
- 722511: Full-service restaurants
- 722512: Limited-service eating places
- 722410: Drinking places (alcoholic beverages)

Usage:
    python scripts/3_test_alcohol_hypothesis_fixed.py
"""

import sys
from pathlib import Path
import pandas as pd
import json

sys.path.append(str(Path(__file__).parent.parent))
from schemas import AlcoholHypothesisTest

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

def analyze_by_category(category_name: str) -> dict:
    """Analyze closure rates for a specific industry category."""
    print(f"\n📊 Analyzing: {category_name}")

    df = pd.read_csv(RAW_DIR / "business_openings_closures.csv")

    # Filter
    df_filtered = df[
        (df['GEO'].str.contains('Toronto', case=False, na=False)) &
        (df['Industry'] == category_name)
    ].copy()

    if len(df_filtered) == 0:
        print(f"   ⚠️  No data found for this category")
        return None

    print(f"   Found {len(df_filtered)} records")

    # Extract year
    df_filtered['year'] = pd.to_datetime(df_filtered['REF_DATE']).dt.year

    # Pivot
    df_pivot = df_filtered.pivot_table(
        index=['year', 'REF_DATE'],
        columns='Business dynamics measure',
        values='VALUE',
        aggfunc='first'
    ).reset_index()

    # Calculate annual rates
    annual = df_pivot.groupby('year').agg({
        'Closing businesses': 'sum',
        'Active businesses': 'mean'
    }).reset_index()

    annual['closure_rate'] = (annual['Closing businesses'] / annual['Active businesses']) * 100

    # Filter complete years (2018-2025)
    annual = annual[(annual['year'] >= 2018) & (annual['year'] <= 2025)]

    # Average rate (excluding 2020 pandemic year)
    avg_rate_excluding_2020 = annual[annual['year'] != 2020]['closure_rate'].mean()
    avg_rate_all = annual['closure_rate'].mean()

    print(f"   Average closure rate (2018-2025): {avg_rate_all:.2f}%")
    print(f"   Average excluding 2020: {avg_rate_excluding_2020:.2f}%")

    return {
        'category': category_name,
        'avg_rate_all': avg_rate_all,
        'avg_rate_excluding_2020': avg_rate_excluding_2020,
        'data': annual
    }

def main():
    print("=" * 70)
    print("ALCOHOL HYPOTHESIS TEST")
    print("=" * 70)
    print("\nHypothesis: Drinking places (bars/pubs) have higher closure rates")
    print("than food-first restaurants")

    # Test with detailed tourism category
    results = {}

    # Full-service restaurants
    print("\n" + "=" * 70)
    print("CATEGORY 1: Full-service restaurants + Limited-service + Drinking places")
    print("(Combined category from tourism breakdown)")
    print("=" * 70)

    tourism_food = analyze_by_category('Food and beverage services (tourism) [722511, 722512, 722410]')

    if tourism_food:
        results['tourism_food'] = tourism_food

    # Try broad accommodation and food services
    print("\n" + "=" * 70)
    print("CATEGORY 2: All Accommodation and Food Services")
    print("(NAICS 72 - broader category)")
    print("=" * 70)

    all_food = analyze_by_category('Accommodation and food services [72]')

    if all_food:
        results['all_food'] = all_food

    # Check what categories are actually available
    print("\n" + "=" * 70)
    print("DATA LIMITATION CHECK")
    print("=" * 70)

    df = pd.read_csv(RAW_DIR / "business_openings_closures.csv")
    toronto = df[df['GEO'].str.contains('Toronto', case=False, na=False)]
    food_related = toronto[toronto['Industry'].str.contains('food|beverage|accommodation|72|drink', case=False, na=False)]

    print("\nFood/beverage categories available in Toronto data:")
    for industry in food_related['Industry'].unique():
        print(f"   - {industry}")

    # Create hypothesis test result
    print("\n" + "=" * 70)
    print("HYPOTHESIS TEST RESULT")
    print("=" * 70)

    if 'tourism_food' in results:
        # We have the combined category but not detailed breakdown
        rate = results['tourism_food']['avg_rate_excluding_2020']

        result = AlcoholHypothesisTest(
            drinking_places_closure_rate=0.0,  # Not available separately
            full_service_restaurants_closure_rate=rate,
            limited_service_closure_rate=None,
            alcohol_hypothesis_supported=False,
            difference_percentage_points=0.0,
            statistical_significance="unclear",
            notes=f"Toronto CMA data combines all food/beverage categories (NAICS 722511, 722512, 722410) into a single 'Food and beverage services (tourism)' category. Average closure rate is {rate:.2f}% (excl. 2020 pandemic). Detailed breakdown by drinking places vs restaurants is NOT available at Toronto CMA level. To test this hypothesis rigorously, would need: (1) Canada-wide data with NAICS detail, OR (2) Hand-coded Layer B analysis of individual closures."
        )

        print("\n⚠️  HYPOTHESIS CANNOT BE TESTED")
        print(f"\n   Combined food/beverage closure rate: {rate:.2f}%")
        print(f"\n   {result.notes}")

    else:
        result = AlcoholHypothesisTest(
            drinking_places_closure_rate=0.0,
            full_service_restaurants_closure_rate=0.0,
            alcohol_hypothesis_supported=False,
            difference_percentage_points=0.0,
            statistical_significance="unclear",
            notes="No suitable data found for Toronto CMA. Detailed NAICS breakdowns not available at city level."
        )

        print("\n❌ NO DATA AVAILABLE")

    # Save results
    output_file = PROCESSED_DIR / "alcohol_hypothesis_results.json"
    with open(output_file, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAY")
    print("=" * 70)
    print("\n✅ Closure rate analysis successful for AGGREGATE food services")
    print("⚠️  Detailed breakdown (bars vs restaurants) NOT available")
    print("\n📌 Options:")
    print("   1. Accept limitation and proceed with aggregate findings")
    print("   2. Use Canada-wide data for NAICS detail (less relevant to Toronto)")
    print("   3. Proceed to Layer B (hand-code individual closures)")

    print("\n" + "=" * 70)
    print("✅ Analysis complete! Run final script:")
    print("   python scripts/4_generate_report.py")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
