"""
Script 1: Fetch Statistics Canada Data

Downloads three key datasets:
1. Business openings and closures (Table 33-10-02700-01)
2. Canadian Business Counts (Table 33-10-07660-01)
3. Food services operating statistics (Table 21-10-0171-01)

All data saved to data/raw/ as CSVs.

Usage:
    python scripts/1_fetch_statcan_data.py
"""

import os
import sys
from pathlib import Path
import requests
import pandas as pd
from datetime import datetime

# Add parent directory to path for schemas import
sys.path.append(str(Path(__file__).parent.parent))
from schemas import DataQualityCheck

# ============================================================================
# Configuration
# ============================================================================

# StatCan table URLs (CSV download links)
STATCAN_TABLES = {
    "business_openings_closures": {
        "table_id": "33-10-0270-01",
        "url": "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDbLoadingData-nonTraduit.action?pid=3310027001&latestN=0&startDate=&endDate=&csvLocale=en&selectedMembers=%5B%5B%5D%5D",
        "description": "Business openings and closures (monthly, Toronto CMA)"
    },
    "business_counts": {
        "table_id": "33-10-0766-01",
        "url": "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDbLoadingData-nonTraduit.action?pid=3310076601&latestN=0&startDate=&endDate=&csvLocale=en&selectedMembers=%5B%5B%5D%5D",
        "description": "Canadian Business Counts (semi-annual, with employees)"
    },
    "food_services_stats": {
        "table_id": "21-10-0171-01",
        "url": "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDbLoadingData-nonTraduit.action?pid=2110017101&latestN=0&startDate=&endDate=&csvLocale=en&selectedMembers=%5B%5B%5D%5D",
        "description": "Food services summary statistics (annual, revenue/expenses/margins)"
    }
}

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"

# ============================================================================
# Fetch Functions
# ============================================================================

def download_statcan_table(table_name: str, table_info: dict) -> pd.DataFrame:
    """
    Download a StatCan table as CSV and return as DataFrame.

    Args:
        table_name: Short name for the table (for logging)
        table_info: Dict with 'url', 'table_id', 'description'

    Returns:
        pandas DataFrame with the table data
    """
    print(f"\n📊 Downloading: {table_info['description']}")
    print(f"   Table ID: {table_info['table_id']}")

    try:
        # Note: StatCan URLs sometimes require session handling or redirect following
        # Using stream=True and following redirects
        response = requests.get(table_info['url'], stream=True, timeout=60)
        response.raise_for_status()

        # Save raw CSV
        output_path = OUTPUT_DIR / f"{table_name}.csv"
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Load as DataFrame
        df = pd.read_csv(output_path)

        print(f"   ✅ Downloaded {len(df):,} rows")
        print(f"   💾 Saved to: {output_path}")

        return df

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error downloading table: {e}")
        print(f"\n   ⚠️  StatCan download may require manual download.")
        print(f"   Please visit: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={table_info['table_id'].replace('-', '')}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None


def validate_data(df: pd.DataFrame, table_name: str, expected_columns: list = None) -> DataQualityCheck:
    """
    Validate downloaded data and return quality check results.

    Args:
        df: DataFrame to validate
        table_name: Name of the table
        expected_columns: Optional list of expected column names

    Returns:
        DataQualityCheck model with validation results
    """
    if df is None or df.empty:
        return DataQualityCheck(
            table_name=table_name,
            rows_fetched=0,
            date_range="N/A",
            naics_codes_present=[],
            quality_issues=["No data fetched"],
            ready_for_analysis=False
        )

    quality_issues = []

    # Check for expected columns
    if expected_columns:
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            quality_issues.append(f"Missing expected columns: {missing_cols}")

    # Check for nulls
    null_counts = df.isnull().sum()
    high_null_cols = null_counts[null_counts > len(df) * 0.5].index.tolist()
    if high_null_cols:
        quality_issues.append(f"High null percentage in: {high_null_cols}")

    # Try to determine date range
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'period' in col.lower() or 'ref' in col.lower()]
    if date_cols:
        try:
            date_range = f"{df[date_cols[0]].min()} to {df[date_cols[0]].max()}"
        except:
            date_range = "Unable to determine"
    else:
        date_range = "No date column found"

    # Try to identify NAICS codes
    naics_cols = [col for col in df.columns if 'naics' in col.lower() or 'industry' in col.lower()]
    if naics_cols:
        naics_codes = df[naics_cols[0]].unique()[:10].tolist()  # First 10 unique values
    else:
        naics_codes = []
        quality_issues.append("No NAICS column identified")

    return DataQualityCheck(
        table_name=table_name,
        rows_fetched=len(df),
        date_range=date_range,
        naics_codes_present=[str(code) for code in naics_codes],
        quality_issues=quality_issues,
        ready_for_analysis=len(quality_issues) == 0
    )


# ============================================================================
# Main
# ============================================================================

def main():
    """
    Main function to download all StatCan tables and validate.
    """
    print("=" * 70)
    print("STATISTICS CANADA DATA FETCHER")
    print("=" * 70)
    print(f"\nOutput directory: {OUTPUT_DIR}")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Download all tables
    results = {}
    quality_checks = []

    for table_name, table_info in STATCAN_TABLES.items():
        df = download_statcan_table(table_name, table_info)
        results[table_name] = df

        # Validate
        check = validate_data(df, table_name)
        quality_checks.append(check)

    # Summary
    print("\n" + "=" * 70)
    print("DATA QUALITY SUMMARY")
    print("=" * 70)

    for check in quality_checks:
        status = "✅ READY" if check.ready_for_analysis else "⚠️  ISSUES"
        print(f"\n{status} {check.table_name}")
        print(f"   Rows: {check.rows_fetched:,}")
        print(f"   Date range: {check.date_range}")
        if check.naics_codes_present:
            print(f"   NAICS codes: {len(check.naics_codes_present)} found")
        if check.quality_issues:
            print(f"   Issues: {', '.join(check.quality_issues)}")

    # Next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)

    if all(check.ready_for_analysis for check in quality_checks):
        print("✅ All data downloaded successfully!")
        print("\nRun next script:")
        print("   python scripts/2_calculate_closure_rates.py")
    else:
        print("⚠️  Some data has quality issues.")
        print("\nOptions:")
        print("1. Manual download: Visit StatCan tables directly and save CSVs to data/raw/")
        print("2. Proceed with available data (some analysis may be limited)")
        print("\nStatCan Table Links:")
        for table_name, table_info in STATCAN_TABLES.items():
            table_id_url = table_info['table_id'].replace('-', '')
            print(f"   - {table_name}: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={table_id_url}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
