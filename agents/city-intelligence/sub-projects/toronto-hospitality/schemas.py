"""
Pydantic schemas for Toronto Hospitality Analysis.

Models for Statistics Canada data:
- Business openings and closures (Table 33-10-02700-01)
- Canadian Business Counts (Table 33-10-07660-01)
- Food services operating statistics (Table 21-10-0171-01)
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Raw StatCan Data Models
# ============================================================================

class BusinessOpeningsClosure(BaseModel):
    """
    Monthly business openings and closures from StatCan Table 33-10-02700-01.

    Example record:
    {
        "period": "2024-01",
        "geography": "Toronto, census metropolitan area",
        "naics": "72 - Accommodation and food services",
        "openings": 120,
        "closures": 95,
        "continuing": 8500
    }
    """
    period: str = Field(..., description="YYYY-MM format")
    geography: str = Field(..., description="Geographic area (e.g., 'Toronto, CMA')")
    naics: str = Field(..., description="NAICS code and description")
    openings: int = Field(..., description="Number of business openings")
    closures: int = Field(..., description="Number of business closures")
    continuing: int = Field(..., description="Number of continuing businesses")

    # Derived
    net_change: Optional[int] = Field(None, description="openings - closures")
    closure_rate: Optional[float] = Field(None, description="closures / continuing")


class CanadianBusinessCount(BaseModel):
    """
    Business counts by NAICS from StatCan Table 33-10-07660-01.

    Provides the denominator for closure rate calculations.
    """
    reference_date: str = Field(..., description="YYYY-MM format")
    geography: str = Field(..., description="Geographic area")
    naics: str = Field(..., description="NAICS code and description")
    establishments_with_employees: int = Field(..., description="Count of establishments")
    employment_size: Optional[str] = Field(None, description="Employment size category if filtered")


class FoodServicesStatistics(BaseModel):
    """
    Operating statistics for food services from StatCan Table 21-10-0171-01.

    Annual data on revenue, expenses, and profit margins.
    """
    year: int = Field(..., description="Reference year")
    naics: str = Field(..., description="NAICS code and description")
    geography: str = Field(default="Canada", description="Geographic area")

    # Financial metrics (in millions of CAD)
    operating_revenue: float = Field(..., description="Operating revenue (millions CAD)")
    operating_expenses: float = Field(..., description="Operating expenses (millions CAD)")
    salaries_wages_benefits: Optional[float] = Field(None, description="Salaries/wages/benefits (millions CAD)")

    # Profitability
    operating_profit_margin: float = Field(..., description="Operating profit margin (%)")


# ============================================================================
# Analysis Models
# ============================================================================

class ClosureRateAnalysis(BaseModel):
    """
    Calculated closure rates over time for a specific category.
    """
    category: str = Field(..., description="Category analyzed (e.g., 'All Food Services', 'Drinking Places')")
    naics: str = Field(..., description="NAICS code")
    time_period: str = Field(..., description="Time period (e.g., '2020-2026')")

    # Metrics
    total_closures: int = Field(..., description="Total closures in period")
    average_annual_closure_rate: float = Field(..., description="Average closure rate (%) per year")
    peak_closure_year: str = Field(..., description="Year with highest closure rate")
    peak_closure_rate: float = Field(..., description="Highest closure rate (%)")

    # Trend
    trend: str = Field(..., description="'accelerating', 'decelerating', 'stable'")
    evidence: str = Field(..., description="Brief summary of evidence")


class AlcoholHypothesisTest(BaseModel):
    """
    Results of testing whether alcohol-heavy businesses (bars) are failing faster.
    """
    drinking_places_closure_rate: float = Field(..., description="Closure rate for NAICS 7224 (%)")
    full_service_restaurants_closure_rate: float = Field(..., description="Closure rate for NAICS 722511 (%)")
    limited_service_closure_rate: Optional[float] = Field(None, description="Closure rate for NAICS 722512 (%)")

    # Comparison
    alcohol_hypothesis_supported: bool = Field(..., description="Are drinking places failing faster?")
    difference_percentage_points: float = Field(..., description="Difference in closure rates")
    statistical_significance: str = Field(..., description="'high', 'medium', 'low', 'unclear'")

    # Context
    notes: str = Field(..., description="Additional context or caveats")


class MarginAnalysis(BaseModel):
    """
    Analysis of profit margin squeeze in food services.
    """
    naics: str = Field(..., description="NAICS category")
    start_year: int = Field(..., description="First year in analysis")
    end_year: int = Field(..., description="Last year in analysis")

    start_margin: float = Field(..., description="Operating margin at start (%)")
    end_margin: float = Field(..., description="Operating margin at end (%)")
    margin_change: float = Field(..., description="Change in margin (percentage points)")

    # Verdict
    margin_squeeze_confirmed: bool = Field(..., description="Is there a margin squeeze?")
    evidence: str = Field(..., description="Brief summary")


class LayerAFindings(BaseModel):
    """
    Complete findings from Layer A macro analysis.

    This is the publishable output.
    """
    report_date: datetime = Field(default_factory=datetime.now)
    geography: str = Field(default="Toronto CMA", description="Geographic area analyzed")
    time_period: str = Field(..., description="Time period covered")

    # Core findings
    structural_reset: ClosureRateAnalysis
    alcohol_hypothesis: AlcoholHypothesisTest
    margin_squeeze: MarginAnalysis

    # Summary
    executive_summary: str = Field(..., description="3-5 sentence summary of key findings")
    key_takeaways: List[str] = Field(..., description="Numbered list of main findings")

    # Metadata
    data_sources: List[str] = Field(..., description="StatCan tables used")
    limitations: List[str] = Field(..., description="Data limitations or caveats")

    # Next steps
    layer_b_recommended: bool = Field(..., description="Should we proceed to Layer B hand-coding?")
    reasoning: str = Field(..., description="Why/why not proceed to Layer B?")


# ============================================================================
# Data Quality Models
# ============================================================================

class DataQualityCheck(BaseModel):
    """
    Validation results for fetched data.
    """
    table_name: str = Field(..., description="StatCan table ID")
    fetch_date: datetime = Field(default_factory=datetime.now)

    rows_fetched: int = Field(..., description="Number of rows")
    date_range: str = Field(..., description="Date range in data")
    naics_codes_present: List[str] = Field(..., description="NAICS codes found")

    quality_issues: List[str] = Field(default_factory=list, description="Any data quality issues")
    ready_for_analysis: bool = Field(..., description="Is data clean enough to analyze?")
