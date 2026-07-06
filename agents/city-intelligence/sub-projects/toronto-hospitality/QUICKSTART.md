# Quickstart Guide: Toronto Hospitality Layer A Analysis

## Goal

Test 3 macro hypotheses with Statistics Canada data:
1. **Structural Reset:** Are closure rates elevated?
2. **Alcohol Hypothesis:** Are bars/pubs dying faster than restaurants?
3. **Margin Squeeze:** Are profit margins declining?

**Time investment:** 1 afternoon of data collection + 1 hour of analysis

---

## Setup (5 minutes)

```bash
# Navigate to project
cd agents/city-intelligence/sub-projects/toronto-hospitality

# Install dependencies
pip install -r requirements.txt
```

---

## Step 1: Get the Data (Manual Download)

The automated download script requires StatCan API credentials. **Manual download is faster:**

### Table 1: Business Openings and Closures
1. Visit: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3310027001
2. **Filter:**
   - Geography: Select "Toronto, census metropolitan area"
   - NAICS: Select "72 - Accommodation and food services" OR "722 - Food services and drinking places"
   - Date: Select all available (2015-present)
3. Click "Download" → CSV format
4. Save as: `data/raw/business_openings_closures.csv`

### Table 2: Canadian Business Counts
1. Visit: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3310076601
2. **Filter:**
   - Geography: "Toronto, census metropolitan area"
   - NAICS: "722 - Food services and drinking places"
   - All available dates
3. Download CSV
4. Save as: `data/raw/business_counts.csv`

### Table 3: Food Services Statistics
1. Visit: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2110017101
2. **Filter:**
   - NAICS: "722 - Food services and drinking places"
   - Geography: Canada (CMA-level not available)
   - All years (2015-present)
3. Download CSV
4. Save as: `data/raw/food_services_stats.csv`

**Expected result:** 3 CSV files in `data/raw/`

---

## Step 2: Run Analysis (10 minutes)

```bash
# Calculate closure rates
python scripts/2_calculate_closure_rates.py

# Test alcohol hypothesis
python scripts/3_test_alcohol_hypothesis.py

# Generate report
python scripts/4_generate_report.py
```

**Outputs:**
- `data/processed/closure_rates_by_year.csv`
- `data/processed/closure_rate_visualization.png`
- `data/processed/alcohol_hypothesis_results.json`
- `ANALYSIS.md` (full report with findings)

---

## Step 3: Read Findings

Open `ANALYSIS.md` to see:
- ✅ Structural reset confirmed?
- ✅ Alcohol hypothesis supported?
- ✅ Margin squeeze detected?
- ✅ Recommendation: Proceed to Layer B or not?

---

## Expected Issues & Solutions

### Issue 1: "No NAICS 7224/722511 data at Toronto CMA level"

**Problem:** StatCan experimental table only reports 2-digit NAICS (72) for CMAs, not 4-digit (7224) or 6-digit (722511).

**Solutions:**
1. **Use national data:** Download Canada-wide data with detailed NAICS
2. **Proceed to Layer B:** Hand-code closures with full detail
3. **Accept limitation:** Test hypotheses with NAICS 72/722 only

### Issue 2: "Margin data not Toronto-specific"

**Expected:** Profitability data only available Canada-wide, not by CMA.

**Impact:** Findings show national trend, not Toronto-specific margin pressure.

### Issue 3: "Date ranges don't align"

**Cause:** Openings/closures (monthly) vs business counts (semi-annual) vs margins (annual)

**Solution:** Scripts aggregate to annual level for comparison.

---

## What Layer A Will Tell You

### If Layer A shows strong signal:
- Closure rates **elevated and accelerating**
- Clear difference between bars and restaurants
- Margins **declining significantly**

→ **Proceed to Layer B:** Hand-code 50 closures to test "experiential vs commodity"

### If Layer A shows weak/no signal:
- Closure rates **stable or unclear**
- No NAICS-level breakdown available
- Margins **stable**

→ **Pivot:** Try qualitative research, different hypothesis, or focus on wellness expansion

---

## Time Savings

| Task | Without Layer A | With Layer A |
|------|-----------------|--------------|
| Data collection | 2-3 weeks hand-coding | 1 hour downloading CSVs |
| Analysis | Manually code 50+ closures | Automated scripts |
| Validation | Anecdotal → hypothesis | Hypothesis → data → validation |
| Cost | ~30 hours | ~2 hours |

**Layer A prevents you from spending 3 weeks on Layer B if the macro signal doesn't exist.**

---

## Next Steps After Layer A

**If proceeding to Layer B:**
1. Scrape closure announcements (BlogTO, CityNews, insauga)
2. Create coding schema: experiential vs commodity
3. Hand-code ~50 closures + matched survivors
4. Statistical comparison

**If pivoting:**
- Focus on wellness boom (inverse of closures)
- Qualitative interviews with owners
- Different market (e.g., Vancouver, Montreal)

---

## Questions?

Check:
- `README.md` - Full project overview
- `schemas.py` - Data models and structure
- Script comments - Detailed inline documentation

**Last updated:** June 2, 2026
