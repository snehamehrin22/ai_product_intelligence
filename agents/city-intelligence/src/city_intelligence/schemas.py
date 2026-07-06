"""
Pydantic schemas for City Intelligence Agent.

These models define the structure of data flowing through the system:
- City data and metadata
- Trends and patterns
- Multi-lens analysis results
- Business insights and recommendations
"""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Core Data Models
# ============================================================================

class City(BaseModel):
    """Represents a city being analyzed."""

    name: str = Field(..., description="City name (e.g., 'Toronto')")
    country: str = Field(..., description="Country (e.g., 'Canada')")
    region: Optional[str] = Field(None, description="Region/province (e.g., 'Ontario')")
    population: Optional[int] = Field(None, description="Current population")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., 'America/Toronto')")
    coordinates: Optional[dict] = Field(None, description="{'lat': 43.65, 'lng': -79.38}")


class DataSource(BaseModel):
    """Represents a data source used in analysis."""

    name: str = Field(..., description="Data source name")
    type: Literal["api", "scrape", "manual", "file"] = Field(..., description="Data collection method")
    url: Optional[str] = Field(None, description="URL if applicable")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last data fetch")
    reliability: Literal["high", "medium", "low"] = Field("medium", description="Data reliability")


class Trend(BaseModel):
    """Represents an observed trend in the city."""

    id: str = Field(..., description="Unique trend ID (slugified name)")
    name: str = Field(..., description="Trend name (e.g., 'Wellness cafe culture in Scarborough')")
    description: str = Field(..., description="Brief description of the trend")
    category: str = Field(..., description="Category (e.g., 'Food & Beverage', 'Retail', 'Lifestyle')")
    neighborhoods: List[str] = Field(default_factory=list, description="Affected neighborhoods")
    demographics: List[str] = Field(default_factory=list, description="Primary demographic groups")
    data_sources: List[DataSource] = Field(default_factory=list, description="Sources for this trend")


# ============================================================================
# 4-Lens Analysis Models
# ============================================================================

class AnthropologyAnalysis(BaseModel):
    """Anthropological lens: culture, rituals, identity, belonging."""

    rituals_behaviors: str = Field(..., description="What rituals/behaviors are forming?")
    identity_shifts: str = Field(..., description="How is identity changing?")
    status_symbols: str = Field(..., description="What signals belonging/status?")
    community_patterns: str = Field(..., description="How are communities forming?")
    cultural_significance: Literal["high", "medium", "low"] = Field(..., description="Cultural importance")


class EconomicsAnalysis(BaseModel):
    """Economics lens: spending power, affordability, wealth distribution."""

    spending_power: str = Field(..., description="Spending capacity by demographic")
    affordability_vs_priority: str = Field(..., description="What can they afford vs what they prioritize?")
    wealth_distribution: str = Field(..., description="How is wealth distributed?")
    economic_anxiety: str = Field(..., description="Signs of economic stress/confidence")
    market_size_estimate: Optional[str] = Field(None, description="Estimated market size if calculable")


class GeopoliticsAnalysis(BaseModel):
    """Geopolitics lens: migration, policy, global dynamics."""

    migration_patterns: str = Field(..., description="Who is moving in/out and why?")
    policy_impacts: str = Field(..., description="How do policies shape this trend?")
    global_local_tension: str = Field(..., description="Global forces vs local adaptation")
    international_influence: str = Field(..., description="How does international context matter?")


class HistoryAnalysis(BaseModel):
    """History lens: evolution, cycles, continuity, rupture."""

    historical_context: str = Field(..., description="How did we get here? What's the backstory?")
    cyclical_vs_new: str = Field(..., description="Is this recurring or genuinely new?")
    continuity_vs_rupture: str = Field(..., description="What's continuous? What's breaking?")
    historical_parallels: str = Field(..., description="Similar patterns in history")


class MultiLensAnalysis(BaseModel):
    """Complete 4-lens analysis of a trend."""

    trend: Trend
    anthropology: AnthropologyAnalysis
    economics: EconomicsAnalysis
    geopolitics: GeopoliticsAnalysis
    history: HistoryAnalysis
    synthesis: str = Field(..., description="Synthesis connecting all 4 lenses")
    analyzed_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Business Intelligence Models
# ============================================================================

class BusinessOpportunity(BaseModel):
    """Actionable business opportunity identified from trend analysis."""

    opportunity_type: Literal["new_business", "expansion", "pivot", "product", "service"]
    description: str = Field(..., description="What business opportunity exists?")
    target_demographic: str = Field(..., description="Who to serve?")
    target_locations: List[str] = Field(..., description="Where to operate? (neighborhoods)")
    positioning: str = Field(..., description="How to message/position?")
    timing: Literal["immediate", "6_months", "12_months", "uncertain"]
    investment_range: Optional[str] = Field(None, description="Est. capital needed (e.g., '$50K-100K')")


class BusinessThreat(BaseModel):
    """Business threat identified from trend analysis."""

    threat_type: Literal["disruption", "decline", "saturation", "regulation", "demographic_shift"]
    description: str = Field(..., description="What is at risk?")
    affected_businesses: List[str] = Field(..., description="Types of businesses at risk")
    severity: Literal["high", "medium", "low"]
    timeline: Literal["immediate", "6_months", "12_months", "long_term"]


class BusinessInsight(BaseModel):
    """Complete business intelligence output for a trend."""

    trend_id: str = Field(..., description="Links to Trend.id")
    opportunities: List[BusinessOpportunity] = Field(default_factory=list)
    threats: List[BusinessThreat] = Field(default_factory=list)
    evidence_strength: Literal["high", "medium", "low"] = Field(..., description="Confidence in analysis")
    confidence_reasoning: str = Field(..., description="Why this confidence level?")
    next_steps: List[str] = Field(..., description="Recommended actions for businesses")


# ============================================================================
# Report Models
# ============================================================================

class CityIntelligenceReport(BaseModel):
    """Complete city intelligence report output."""

    city: City
    report_date: datetime = Field(default_factory=datetime.now)
    time_period: str = Field(..., description="Period analyzed (e.g., 'Q2 2026', 'May 2026')")

    # Trends and analysis
    trends: List[MultiLensAnalysis] = Field(..., description="All trends with 4-lens analysis")
    business_insights: List[BusinessInsight] = Field(..., description="Business recommendations")

    # Metadata
    data_sources_used: List[DataSource] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list, description="Data gaps or limitations")

    # Summary
    executive_summary: str = Field(..., description="High-level overview for executives")
    top_opportunities: List[str] = Field(..., description="Top 5 opportunities identified")
    top_threats: List[str] = Field(..., description="Top 5 threats identified")


# ============================================================================
# API Response Models (for LLM structured output)
# ============================================================================

class LensAnalysisResponse(BaseModel):
    """Wrapper for LLM responses to ensure valid JSON."""

    analysis: dict = Field(..., description="Analysis content (varies by lens)")
    confidence: Literal["high", "medium", "low"] = Field("medium")
    sources_cited: List[str] = Field(default_factory=list)


class BusinessInsightResponse(BaseModel):
    """Wrapper for business insight generation."""

    opportunities: List[dict] = Field(default_factory=list)
    threats: List[dict] = Field(default_factory=list)
    evidence_strength: Literal["high", "medium", "low"] = Field("medium")
    reasoning: str = Field(..., description="Why this assessment?")


# ============================================================================
# Neighborhood Intelligence Models
# ============================================================================

class NeighborhoodIdentity(BaseModel):
    """Section 1: Neighborhood Identity - how the neighborhood sees itself and is seen by others."""

    known_for: str = Field(..., description="What is this neighborhood known for?")
    resident_description: str = Field(..., description="How would residents describe it?")
    outsider_description: str = Field(..., description="How would outsiders describe it?")
    emotions_evoked: str = Field(..., description="What emotions does it evoke?")
    cultural_uniqueness: str = Field(..., description="What makes it culturally unique?")
    defining_values: str = Field(..., description="What values define this place?")
    stereotypes: str = Field(..., description="What stereotypes exist?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class HistoricalEvolution(BaseModel):
    """Section 2: Historical Evolution - how the neighborhood developed over time."""

    development_history: str = Field(..., description="How did this neighborhood develop?")
    major_events: str = Field(..., description="Major historical events that shaped it")
    immigration_history: str = Field(..., description="Immigration waves and cultural influences")
    shaping_industries: str = Field(..., description="Industries that shaped the neighborhood")
    turning_points: str = Field(..., description="Major turning points in evolution")
    gentrification_patterns: str = Field(..., description="Gentrification or redevelopment patterns")
    business_evolution: str = Field(..., description="How has the business landscape evolved?")
    identity_changes: str = Field(..., description="How has the identity changed over time?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class DemographicAnalysis(BaseModel):
    """Section 3: Demographic Shifts - population characteristics and changes."""

    population_growth: str = Field(..., description="Population growth patterns and trends")
    age_distribution: str = Field(..., description="Age demographics and distribution")
    income_levels: str = Field(..., description="Income levels and distribution")
    education_levels: str = Field(..., description="Education attainment")
    household_composition: str = Field(..., description="Household types and sizes")
    renters_vs_owners: str = Field(..., description="Housing tenure patterns")
    housing_types: str = Field(..., description="Types of housing stock")
    household_size: str = Field(..., description="Average household sizes")
    immigration_patterns: str = Field(..., description="Recent immigration trends")
    languages_spoken: str = Field(..., description="Language diversity")
    family_structure: str = Field(..., description="Family structures and dynamics")
    business_influence: str = Field(..., description="How do these changes influence local businesses?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class EconomicLandscape(BaseModel):
    """Section 4: Economic Landscape - financial forces shaping the neighborhood."""

    commercial_rents: str = Field(..., description="Commercial rent levels and trends")
    residential_rents: str = Field(..., description="Residential rent levels")
    office_occupancy: str = Field(..., description="Office space occupancy rates")
    remote_work_impact: str = Field(..., description="Impact of remote work on the area")
    major_employers: str = Field(..., description="Major employers in/near the area")
    employment_mix: str = Field(..., description="Mix of employment types")
    consumer_spending: str = Field(..., description="Consumer spending patterns")
    vacancy_rates: str = Field(..., description="Commercial vacancy rates")
    independent_vs_chains: str = Field(..., description="Independent businesses vs chains ratio")
    luxury_vs_budget: str = Field(..., description="Luxury vs budget business presence")
    economic_forces: str = Field(..., description="Which economic forces are shaping demand?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class BusinessEcosystem(BaseModel):
    """Section 5: Business Ecosystem - how businesses cluster and interact."""

    business_mix: str = Field(..., description="Map of surrounding business types (cafés, restaurants, bars, fitness, retail, etc.)")
    clustering_patterns: str = Field(..., description="Why do these businesses cluster together?")
    reinforcement: str = Field(..., description="Which businesses reinforce each other?")
    competition: str = Field(..., description="Which businesses compete for attention?")
    foot_traffic_drivers: str = Field(..., description="Which businesses increase foot traffic for others?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class HumanMovement(BaseModel):
    """Section 6: Human Movement - how people move through the neighborhood."""

    morning_patterns: str = Field(..., description="Morning movement patterns")
    lunch_patterns: str = Field(..., description="Lunchtime activity")
    afternoon_patterns: str = Field(..., description="Afternoon movement")
    evening_patterns: str = Field(..., description="Evening activity")
    weekend_patterns: str = Field(..., description="Weekend behavior")
    tourist_patterns: str = Field(..., description="Tourist movement and behavior")
    commuter_patterns: str = Field(..., description="Commuter flows")
    resident_patterns: str = Field(..., description="Resident daily rhythms")
    student_patterns: str = Field(..., description="Student activity if applicable")
    worker_patterns: str = Field(..., description="Office worker patterns")
    foot_traffic_origin: str = Field(..., description="Where does foot traffic originate?")
    foot_traffic_destination: str = Field(..., description="Where does it end?")
    highest_activity_streets: str = Field(..., description="Which streets have the highest activity?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class ThirdPlaceAnalysis(BaseModel):
    """Section 7: Third Place Analysis - using Ray Oldenburg's framework."""

    third_place_adequacy: str = Field(..., description="Does this neighborhood have enough third places?")
    gathering_spots: str = Field(..., description="Where do people gather?")
    lingering_spots: str = Field(..., description="Where do people linger?")
    stranger_interaction: str = Field(..., description="Where do strangers interact?")
    community_formation: str = Field(..., description="Where do communities form?")
    existing_social_infrastructure: str = Field(..., description="What social infrastructure already exists?")
    missing_infrastructure: str = Field(..., description="What is missing?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class BehavioralPatterns(BaseModel):
    """Section 8: Behavioral Patterns - recurring neighborhood behaviors."""

    recurring_behaviors: str = Field(..., description="Recurring behaviors (morning coffee walks, weekend brunch, dog walking, remote work, running, cycling, etc.)")
    neighborhood_rhythms: str = Field(..., description="Explain the rhythms of the neighborhood")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class CulturalSignals(BaseModel):
    """Section 9: Cultural Signals - values expressed through the neighborhood."""

    expressed_values: str = Field(..., description="Values expressed (health, luxury, convenience, creativity, community, sustainability, etc.)")
    value_manifestations: str = Field(..., description="How do these values appear in everyday life?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class MacroTrends(BaseModel):
    """Section 10: Macro Trends - broader trends shaping the neighborhood."""

    shaping_trends: str = Field(..., description="Broader trends shaping this neighborhood (hybrid work, housing affordability, immigration, wellness culture, etc.)")
    accelerating_trends: str = Field(..., description="Which trends are accelerating?")
    declining_trends: str = Field(..., description="Which trends are declining?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class NeighborhoodNeed(BaseModel):
    """A single unmet neighborhood need."""

    need: str = Field(..., description="Description of the unmet need")
    evidence: str = Field(..., description="Evidence supporting this need")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level")


class NeighborhoodNeeds(BaseModel):
    """Section 11: Neighborhood Needs - unmet needs identified."""

    unmet_needs: List[NeighborhoodNeed] = Field(..., description="Unmet needs ranked by confidence")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class FutureOutlook(BaseModel):
    """Section 12: Future Outlook - how the neighborhood will likely change."""

    three_year_outlook: str = Field(..., description="How will this neighborhood change in 3 years?")
    five_year_outlook: str = Field(..., description="How will this neighborhood change in 5 years?")
    ten_year_outlook: str = Field(..., description="How will this neighborhood change in 10 years?")
    population_changes: str = Field(..., description="Expected population changes")
    housing_changes: str = Field(..., description="Expected housing changes")
    transit_changes: str = Field(..., description="Expected transit changes")
    retail_changes: str = Field(..., description="Expected retail changes")
    commercial_changes: str = Field(..., description="Expected commercial development")
    cultural_changes: str = Field(..., description="Expected cultural changes")
    technology_changes: str = Field(..., description="Expected technology impacts")
    consumer_behavior_changes: str = Field(..., description="Expected consumer behavior changes")
    business_types_to_succeed: str = Field(..., description="What types of businesses are most likely to succeed?")
    cafe_implications: str = Field(..., description="What does this mean for a café operator?")


class CafeImplications(BaseModel):
    """Section 13: Implications for Cafés - specific to café operations."""

    ideal_cafe_type: str = Field(..., description="What type of café is most likely to thrive?")
    ideal_customer: str = Field(..., description="Who is the ideal customer?")
    ideal_experience: str = Field(..., description="What experience should the café create?")
    product_priorities: str = Field(..., description="What products should it prioritize?")
    what_to_avoid: str = Field(..., description="What should it avoid?")
    differentiation: str = Field(..., description="What would differentiate it?")


class StrategicInsights(BaseModel):
    """Section 14: Strategic Insights - advice for entrepreneurs."""

    pre_lease_insights: str = Field(..., description="What should they understand before signing a lease?")
    outsider_mistakes: str = Field(..., description="What mistakes would outsiders make?")
    critical_dynamics: str = Field(..., description="What neighborhood dynamics matter most?")
    invisible_opportunities: str = Field(..., description="What opportunities are invisible at first glance?")


class NeighborhoodIntelligenceReport(BaseModel):
    """Section 15: Complete neighborhood intelligence report."""

    # Metadata
    neighborhood_name: str = Field(..., description="Neighborhood name")
    city: City
    report_date: datetime = Field(default_factory=datetime.now)
    time_period: str = Field(..., description="Period analyzed (e.g., 'June 2026')")

    # 15 Sections
    identity: NeighborhoodIdentity
    historical_evolution: HistoricalEvolution
    demographics: DemographicAnalysis
    economics: EconomicLandscape
    business_ecosystem: BusinessEcosystem
    human_movement: HumanMovement
    third_places: ThirdPlaceAnalysis
    behavioral_patterns: BehavioralPatterns
    cultural_signals: CulturalSignals
    macro_trends: MacroTrends
    neighborhood_needs: NeighborhoodNeeds
    future_outlook: FutureOutlook
    cafe_implications: CafeImplications
    strategic_insights: StrategicInsights

    # Executive Summary
    neighborhood_story: str = Field(..., description="What is the story of this neighborhood?")
    defining_human_needs: str = Field(..., description="What human needs define it?")
    defining_economic_forces: str = Field(..., description="What economic forces define it?")
    defining_cultural_forces: str = Field(..., description="What cultural forces define it?")
    cafe_success_factors: str = Field(..., description="Why do certain cafés succeed here while others fail?")
    one_sentence_summary: str = Field(..., description="If you had to describe this neighborhood in one sentence, what would it be?")

    # Data sources and limitations
    data_sources_used: List[DataSource] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list, description="Data gaps or limitations")
