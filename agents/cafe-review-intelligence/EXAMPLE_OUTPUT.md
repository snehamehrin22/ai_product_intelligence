# Example Output

Here's what the JSON files look like after analyzing a cafe.

## Terminal Output

```
🔍 Cafe Review Intelligence Agent

Analyzing: Quantum Coffee (Toronto)

Step 1: Scraping reviews from Google Maps...
✓ Found 45 reviews
Average rating: 4.3/5.0
Date range: 2025-01-15 to 2026-06-15

Step 2: Detecting behavioral signals...
✓ Detected 32 behavioral signals

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Signal Type        ┃ Count ┃ Sample Keywords          ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ loyalty            │ 12    │ my spot, regular, always │
│ first_timer        │ 8     │ first time, confusing    │
│ churn              │ 5     │ used to, went downhill   │
│ social_mention     │ 7     │ instagram, photo         │
└────────────────────┴───────┴──────────────────────────┘

Step 3: Generating actionable insights...
✓ Generated 5 insights across 3 priority areas

🎯 Top 3 Priority Findings:

┌─ Finding #1 ────────────────────────────────────────┐
│ Layer: ONBOARDING                                   │
│                                                     │
│ Finding: 35% of first-time visitors (8 reviews)    │
│ mention confusion during ordering, specifically     │
│ around menu board readability and where to order.   │
│                                                     │
│ Sentiment: negative | Evidence: 8 mentions |        │
│ Confidence: medium                                  │
│                                                     │
│ Recommended Experiment:                             │
│ Install clear signage showing: (1) menu sections   │
│ with descriptions, (2) ordering flow, (3) first-   │
│ timer special offer. Train staff to proactively    │
│ greet anyone who hesitates for >10 seconds.        │
│ Measure: % of first-time visitors who return       │
│ within 7 days (baseline vs. test period).          │
│                                                     │
│ Expected Impact:                                    │
│ Reduce first-visit friction, increase 7-day        │
│ return rate from 12% to 20%+, decrease negative   │
│ reviews mentioning "confusing" by 50%.             │
└─────────────────────────────────────────────────────┘

[... 2 more findings ...]

Step 4: Saving results to JSON files...
✓ Saved reviews to: quantum_coffee_reviews_20260616_211500.json
✓ Saved signals to: quantum_coffee_signals_20260616_211500.json
✓ Saved analysis to: quantum_coffee_analysis_20260616_211500.json

✅ Analysis complete!

Cafe: Quantum Coffee
Reviews analyzed: 45
Signals detected: 32
Insights generated: 3

Results saved in: data/
```

## JSON File Examples

### 1. Reviews File (`quantum_coffee_reviews_20260616_211500.json`)

```json
{
  "cafe_name": "Quantum Coffee",
  "location": "Toronto",
  "total_reviews": 45,
  "average_rating": 4.3,
  "date_range_start": "2025-01-15T10:23:00+00:00",
  "date_range_end": "2026-06-15T14:35:00+00:00",
  "scraped_at": "2026-06-16T21:15:00+00:00",
  "reviews": [
    {
      "rating": 5,
      "text": "This is my regular spot! Sarah the barista knows my name and order. I come here every morning before work.",
      "date": "2026-06-10T09:15:00+00:00",
      "reviewer_name": "John D.",
      "source": "Google Maps"
    },
    {
      "rating": 2,
      "text": "Used to love this place but quality went downhill. Coffee tastes burnt now.",
      "date": "2026-06-08T11:20:00+00:00",
      "reviewer_name": "Jane S.",
      "source": "Google Maps"
    }
    // ... 43 more reviews
  ]
}
```

### 2. Signals File (`quantum_coffee_signals_20260616_211500.json`)

```json
{
  "cafe_name": "Quantum Coffee",
  "total_signals": 32,
  "detected_at": "2026-06-16T21:15:00+00:00",
  "signals_by_type": {
    "loyalty": {
      "count": 12,
      "signals": [
        {
          "keywords": ["my spot", "regular"],
          "excerpt": "...This is my regular spot! Sarah the barista knows my name...",
          "review_rating": 5,
          "review_date": "2026-06-10T09:15:00+00:00"
        }
        // ... 11 more
      ]
    },
    "churn": {
      "count": 5,
      "signals": [
        {
          "keywords": ["used to", "went downhill"],
          "excerpt": "...Used to love this place but quality went downhill...",
          "review_rating": 2,
          "review_date": "2026-06-08T11:20:00+00:00"
        }
        // ... 4 more
      ]
    }
    // ... other signal types
  }
}
```

### 3. Analysis File (`quantum_coffee_analysis_20260616_211500.json`)

```json
{
  "cafe_name": "Quantum Coffee",
  "total_reviews_analyzed": 45,
  "date_range": "2025-01-15 to 2026-06-15",
  "generated_at": "2026-06-16T21:15:00+00:00",

  "top_3_findings": [
    {
      "framework_layer": "onboarding",
      "finding": "35% of first-time visitors (8 reviews) mention confusion during ordering, specifically around menu board readability and where to order.",
      "sentiment": "negative",
      "evidence_count": 8,
      "confidence": "medium",
      "sample_reviews": [
        "First time here and menu was confusing",
        "Didn't know where to order, felt lost",
        "Beautiful space but overwhelming menu board"
      ],
      "recommended_experiment": "Install clear signage showing: (1) menu sections with descriptions, (2) ordering flow ('Order here → Pick up there'), (3) first-timer special offer ('New here? Ask us for recommendations'). Train staff to proactively greet anyone who hesitates for >10 seconds. Measure: % of first-time visitors who return within 7 days (baseline vs. test period).",
      "expected_impact": "Reduce first-visit friction, increase 7-day return rate from current 12% to 20%+, and decrease negative reviews mentioning 'confusing' by 50%."
    },
    {
      "framework_layer": "retention",
      "finding": "12 reviews mention specific barista names (Sarah, Mike), indicating strong staff-customer relationships as a retention driver.",
      "sentiment": "positive",
      "evidence_count": 12,
      "confidence": "high",
      "sample_reviews": [
        "Sarah the barista knows my order",
        "Mike always remembers my name",
        "The staff here make it feel like home"
      ],
      "recommended_experiment": "Formalize 'named drinks for regulars' program: Staff track regular customers' preferred drinks, give them personalized names ('The Sarah Special'), display on a 'Regulars Board' behind counter. Track: % of customers who become 'named regulars' within 30 days, repeat visit frequency of named regulars vs. non-named.",
      "expected_impact": "Strengthen loyalty loop, increase weekly visit frequency from 2.1 to 2.8 visits/week for enrolled customers, create Instagram-worthy content moment ('I have my own drink!')."
    }
    // ... 1 more finding
  ],

  "insights_by_layer": {
    "onboarding": [
      // ... insights for onboarding layer
    ],
    "activation": [
      // ... insights for activation layer
    ],
    "retention": [
      // ... insights for retention layer
    ],
    "monetization": [
      // ... insights for monetization layer
    ],
    "social": [
      // ... insights for social layer
    ]
  },

  "summary": {
    "total_insights": 5,
    "insights_per_layer": {
      "onboarding": 1,
      "activation": 0,
      "retention": 2,
      "monetization": 1,
      "social": 1
    }
  }
}
```

## What to Do With These Files

1. **For reels:** Use top 3 findings as content hooks
2. **For consulting:** Send `*_analysis.json` to cafe owners as a deliverable
3. **For tracking:** Compare analysis files over time (run monthly)
4. **For patterns:** Aggregate signals across multiple cafes to spot trends
5. **For experiments:** Use recommended experiments as consulting roadmap

## File Naming Pattern

Files use this format: `{cafe_name}_{type}_{timestamp}.json`

- **cafe_name:** Sanitized (lowercase, underscores, alphanumeric only)
- **type:** `reviews`, `signals`, or `analysis`
- **timestamp:** `YYYYMMDD_HHMMSS`

Example: `quantum_coffee_analysis_20260616_211500.json`

This makes it easy to:
- Sort chronologically
- Find latest analysis: `ls -t quantum_coffee_analysis_*.json | head -1`
- Track changes: Compare files from different dates
