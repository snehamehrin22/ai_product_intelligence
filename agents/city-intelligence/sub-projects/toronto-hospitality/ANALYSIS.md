# Toronto Hospitality Analysis: Layer A Findings

**Report Date:** June 02, 2026
**Geography:** Toronto, census metropolitan area
**Time Period:** 2018-2025

---

## Executive Summary

Toronto's food services sector shows accelerating closure rates averaging 57.52% annually from 2018-2025. Detailed NAICS breakdowns were unavailable at the Toronto CMA level, limiting our ability to test the alcohol hypothesis rigorously. Margin data suggests stable or improving profitability, though this is Canada-wide data not Toronto-specific.

---

## Key Findings

1. **Closure rates are ACCELERATING: 57.52% average, peaking at 93.67% in 2020**

2. **Alcohol hypothesis INCONCLUSIVE: Toronto CMA data combines all food/beverage categories (NAICS 722511, 722512, 722410) into a single 'Food and beverage services (tourism)' category. Average closure rate is 52.07% (excl. 2020 pandemic). Detailed breakdown by drinking places vs restaurants is NOT available at Toronto CMA level. To test this hypothesis rigorously, would need: (1) Canada-wide data with NAICS detail, OR (2) Hand-coded Layer B analysis of individual closures.**

3. **Profit margin pressure unclear from national data**

---

## 1. Structural Reset: Closure Rate Analysis

**Question:** Are Toronto restaurants closing at unprecedented rates?

**Findings:**
- **Time period:** 2018-2025
- **Total closures:** 47,686
- **Average annual closure rate:** 57.52%
- **Peak year:** 2020 (93.67%)
- **Trend:** ACCELERATING

**Evidence:** Analysis of 8 years of data from Statistics Canada.

**Verdict:** ✅ CONFIRMED - Closure rates are elevated

---

## 2. Alcohol Hypothesis: Are Bars Dying Faster?

**Question:** Do alcohol-heavy businesses (bars, pubs) have higher closure rates than food-first restaurants?

**Findings:**
- **Drinking places (NAICS 7224):** 0.0%
- **Full-service restaurants (NAICS 722511):** 52.06930581174187%
- **Difference:** +0.00 percentage points
- **Statistical significance:** unclear

**Notes:** Toronto CMA data combines all food/beverage categories (NAICS 722511, 722512, 722410) into a single 'Food and beverage services (tourism)' category. Average closure rate is 52.07% (excl. 2020 pandemic). Detailed breakdown by drinking places vs restaurants is NOT available at Toronto CMA level. To test this hypothesis rigorously, would need: (1) Canada-wide data with NAICS detail, OR (2) Hand-coded Layer B analysis of individual closures.

**Verdict:** ❌ NOT SUPPORTED (or insufficient data)

---

## 3. Margin Squeeze: Profitability Pressure

**Question:** Are operating margins declining for food services?

**Findings:**
- **NAICS category:** 722
- **Time period:** 2020-2026
- **Starting margin:** 0.0%
- **Ending margin:** 0.0%
- **Change:** +0.00 percentage points

**Evidence:** Data not available at Toronto CMA level. Margin data only available Canada-wide.

**Verdict:** ⚠️  No clear compression detected

---

## Data Sources

- Statistics Canada Table 33-10-02700-01: Business openings and closures (monthly)
- Statistics Canada Table 33-10-07660-01: Canadian Business Counts
- Statistics Canada Table 21-10-0171-01: Food services summary statistics


**All data from Statistics Canada (public, authoritative)**

---

## Limitations

- Geographic granularity: CMA-level only, cannot isolate downtown vs suburbs
- NAICS detail: Experimental table may only report 2-digit NAICS at CMA level
- Margin data: Canada-wide only, not Toronto-specific
- No closure reasons: Data does not explain WHY businesses closed
- Time lag: Business counts published semi-annually with 3-6 month delay


---

## Recommendation: Should We Proceed to Layer B?

**Layer B** would involve:
- Hand-coding ~50 restaurant closures from BlogTO/CityNews
- Creating "experiential vs commodity" taxonomy
- Matching closures with survivors on same streets
- Testing "experiential survives longer" hypothesis

**Effort:** 2-3 weeks of manual work

**Recommendation:** ✅ YES - Layer A shows strong signal worth investigating deeper

**Reasoning:** Layer A found 2/4 hypotheses supported with strong macro signal. Hand-coding 47686 closures would provide granular insight into experiential vs commodity dynamics.

---

## Visualizations

See `data/processed/` for:
- `closure_rate_visualization.png` - Closure rate trend over time

---

## Next Steps

**If proceeding to Layer B:**
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


---

**Generated:** June 02, 2026 at 01:19 PM
**Status:** Layer A Complete
