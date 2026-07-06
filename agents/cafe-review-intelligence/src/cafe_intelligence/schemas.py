"""
Pydantic schemas for cafe review intelligence.

All data validation happens here - this is the single source of truth.
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Review Models
# ============================================================================

class Review(BaseModel):
    """A single Google review."""

    cafe_name: str = Field(..., description="Name of the cafe")
    rating: int = Field(..., ge=1, le=5, description="Star rating 1-5")
    text: str = Field(..., min_length=1, description="Review text")
    date: datetime = Field(..., description="When review was posted")
    reviewer_name: Optional[str] = Field(None, description="Name of reviewer")

    # Metadata
    source: str = Field(default="Google Maps", description="Review source")
    scraped_at: datetime = Field(default_factory=datetime.now, description="When we scraped this")


class ReviewBatch(BaseModel):
    """Collection of reviews for a cafe."""

    cafe_name: str
    location: str
    reviews: List[Review] = Field(default_factory=list)  # Allow empty list
    total_reviews: int
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0)  # Allow 0 for no reviews
    date_range_start: datetime
    date_range_end: datetime


# ============================================================================
# Retention Signal Models
# ============================================================================

class RetentionSignal(BaseModel):
    """A behavioral signal detected in review text."""

    signal_type: Literal["loyalty", "churn", "first_timer", "repeat", "onboarding_issue",
                         "pricing_mention", "social_mention"] = Field(
        ..., description="Type of behavioral signal"
    )
    keywords: List[str] = Field(..., min_items=1, description="Keywords that triggered this signal")
    excerpt: str = Field(..., min_length=10, description="Relevant excerpt from review")
    review_rating: int = Field(..., ge=1, le=5, description="Rating of the review this came from")
    review_date: datetime = Field(..., description="Date of the review")

    # Context
    cafe_name: str
    detected_at: datetime = Field(default_factory=datetime.now)


class SignalSummary(BaseModel):
    """Aggregated signals for a cafe."""

    cafe_name: str
    signal_type: str
    count: int = Field(..., ge=0)
    sample_excerpts: List[str] = Field(..., max_items=5, description="Up to 5 example excerpts")
    keywords_found: List[str] = Field(..., description="All keywords found for this signal type")


# ============================================================================
# Behavioral Framework Models
# ============================================================================

class BehavioralInsight(BaseModel):
    """An actionable insight mapped to the 5-layer framework."""

    framework_layer: Literal["onboarding", "activation", "retention", "monetization", "social"] = Field(
        ..., description="Which layer of the framework this insight relates to"
    )

    # The finding
    finding: str = Field(..., min_length=20, description="What pattern we observed")
    sentiment: Literal["positive", "negative", "mixed"] = Field(..., description="Overall sentiment")
    evidence_count: int = Field(..., ge=1, description="How many reviews support this finding")
    confidence: Literal["high", "medium", "low"] = Field(..., description="How confident we are")

    # Supporting evidence
    sample_reviews: List[str] = Field(..., min_items=1, max_items=3,
                                     description="1-3 example review excerpts")

    # Actionable experiment
    recommended_experiment: str = Field(..., min_length=30,
                                       description="Specific experiment to test this hypothesis")
    expected_impact: str = Field(..., description="What success would look like")

    # Metadata
    cafe_name: str
    generated_at: datetime = Field(default_factory=datetime.now)


class FrameworkAnalysis(BaseModel):
    """Complete analysis of a cafe through the 5-layer framework."""

    cafe_name: str

    # Insights by layer
    onboarding_insights: List[BehavioralInsight] = Field(default_factory=list)
    activation_insights: List[BehavioralInsight] = Field(default_factory=list)
    retention_insights: List[BehavioralInsight] = Field(default_factory=list)
    monetization_insights: List[BehavioralInsight] = Field(default_factory=list)
    social_insights: List[BehavioralInsight] = Field(default_factory=list)

    # Top priorities
    top_3_findings: List[BehavioralInsight] = Field(..., min_items=1, max_items=3,
                                                   description="Top 3 most important findings")

    # Summary stats
    total_reviews_analyzed: int
    date_range: str
    generated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Experiment Models
# ============================================================================

class Experiment(BaseModel):
    """A recommended experiment for a cafe."""

    cafe_name: str
    framework_layer: Literal["onboarding", "activation", "retention", "monetization", "social"]

    # The experiment
    experiment_name: str = Field(..., min_length=10)
    hypothesis: str = Field(..., description="What we think will happen and why")
    implementation: str = Field(..., description="Exactly how to run this experiment")

    # Measurement
    success_metric: str = Field(..., description="Single metric to track")
    target: str = Field(..., description="What success looks like (e.g., '+20% repeat visits')")
    duration: str = Field(..., description="How long to run (e.g., '4 weeks')")

    # Supporting evidence
    based_on_finding: str = Field(..., description="Which insight this experiment addresses")
    evidence_count: int = Field(..., ge=1, description="How many reviews support this")

    # Metadata
    priority: Literal["high", "medium", "low"] = Field(...)
    estimated_difficulty: Literal["easy", "medium", "hard"] = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Weekly Digest Model
# ============================================================================

class WeeklyDigest(BaseModel):
    """Weekly digest for multiple cafes."""

    week_start: datetime
    week_end: datetime
    cafes_analyzed: List[str]

    # Cross-cafe patterns
    trending_issues: List[str] = Field(..., description="Issues appearing across multiple cafes")
    trending_praise: List[str] = Field(..., description="Praise appearing across multiple cafes")

    # Individual cafe summaries
    cafe_analyses: List[FrameworkAnalysis]

    # Meta insights
    total_reviews_analyzed: int
    generated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Keyword Detection Config
# ============================================================================

class KeywordConfig(BaseModel):
    """Configuration for behavioral keyword detection."""

    # Retention signals
    loyalty_keywords: List[str] = Field(
        default=[
            "my spot", "my place", "regular", "always come here", "favorite",
            "go-to", "never disappoints", "consistently", "every time", "staff know me",
            "barista knows", "they remember"
        ]
    )

    churn_keywords: List[str] = Field(
        default=[
            "used to", "not anymore", "went downhill", "changed", "inconsistent",
            "not as good", "disappointed", "won't be back", "last time",
            "quality dropped", "not worth it anymore"
        ]
    )

    first_timer_keywords: List[str] = Field(
        default=[
            "first time", "first visit", "never been", "heard about",
            "wanted to try", "finally tried", "confusing", "didn't know",
            "unclear", "overwhelming menu"
        ]
    )

    repeat_keywords: List[str] = Field(
        default=[
            "came back", "second time", "third time", "returned", "again",
            "back within", "visited twice", "multiple times", "frequent visitor"
        ]
    )

    # Onboarding signals
    onboarding_issue_keywords: List[str] = Field(
        default=[
            "confusing", "unclear", "didn't know how", "hard to find",
            "overwhelming", "intimidating", "no signage", "where to order",
            "what to order", "staff didn't explain"
        ]
    )

    # Monetization signals
    pricing_keywords: List[str] = Field(
        default=[
            "expensive", "pricey", "worth it", "overpriced", "cheap",
            "good value", "affordable", "bundle", "deal", "membership",
            "loyalty card", "subscription"
        ]
    )

    # Social signals
    social_keywords: List[str] = Field(
        default=[
            "instagram", "photo", "aesthetic", "beautiful", "gorgeous space",
            "instagrammable", "picture perfect", "photogenic", "posted about",
            "shared on", "perfect for photos"
        ]
    )
