"""
Pydantic schemas for Forno SSR implementation.

Single source of truth for all data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class IncomeLevel(str, Enum):
    """Income level categories matching survey data."""
    STRUGGLING = "struggling"
    MANAGING = "managing"
    COMFORTABLE = "comfortable"
    AFFLUENT = "affluent"


class Persona(BaseModel):
    """
    A synthetic consumer persona based on King Street regulars.

    Represents a typical Forno Cultura customer profile.
    """
    persona_id: str = Field(..., description="Unique identifier (e.g., 'p1')")
    age: int = Field(..., ge=18, le=80, description="Age in years")
    role: str = Field(..., min_length=2, description="Occupation/role (e.g., 'tech worker')")
    income_level: IncomeLevel = Field(..., description="Income bracket")
    visit_frequency: str = Field(..., description="How often they visit (e.g., '3-4 lunches/week')")
    current_behavior: str = Field(..., description="What they currently buy/do at Forno")
    location: str = Field(default="King Street West, Toronto", description="Location context")

    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "p1",
                "age": 27,
                "role": "tech worker at King West startup",
                "income_level": "comfortable",
                "visit_frequency": "3-4 lunches per week",
                "current_behavior": "gets coffee and sandwich for lunch",
                "location": "King Street West, Toronto"
            }
        }


class SubscriptionConcept(BaseModel):
    """
    A subscription product concept to be tested.

    Defines what's being offered and at what value proposition.
    """
    concept_id: str = Field(..., description="Unique identifier (e.g., 'c1')")
    name: str = Field(..., min_length=3, description="Concept name")
    description: str = Field(..., min_length=10, description="What's included")
    price_point: str = Field(..., description="Pricing structure (e.g., '$45/month')")
    value_props: List[str] = Field(..., min_items=1, description="Key value propositions")
    target_behavior: str = Field(..., description="What customer behavior this serves")

    class Config:
        json_schema_extra = {
            "example": {
                "concept_id": "c1",
                "name": "King West Sandwich + Coffee Pass",
                "description": "8 sandwiches + 8 coffees per month at King Street location",
                "price_point": "$120/month (save ~$40)",
                "value_props": [
                    "Never wait in line - priority pickup",
                    "Guaranteed fresh panini daily",
                    "Works out to $7.50 per combo vs $10 regular"
                ],
                "target_behavior": "Lunch regulars who visit 2+ times per week"
            }
        }


class LikertAnchor(BaseModel):
    """
    Reference statement for a specific Likert scale rating.

    Used to map free-text responses to numerical ratings via semantic similarity.
    """
    rating: int = Field(..., ge=1, le=5, description="Likert scale rating (1-5)")
    statement: str = Field(..., min_length=10, description="Reference statement text")
    anchor_set_id: int = Field(..., description="Which set of anchors this belongs to")

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "statement": "This fits perfectly into my weekly King Street visits; I can see myself keeping it for months.",
                "anchor_set_id": 0
            }
        }


class SyntheticResponse(BaseModel):
    """
    Free-text response from LLM about subscription intent.

    This is the raw output before SSR mapping.
    """
    persona_id: str
    concept_id: str
    response_text: str = Field(..., min_length=10, description="Free-text explanation of intent")
    sample_number: int = Field(..., ge=1, description="Which sample (1 or 2)")

    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "p1",
                "concept_id": "c1",
                "response_text": "I'd probably subscribe. I'm at Forno 3-4 times a week for lunch anyway, and $120/month is less than I currently spend. The priority pickup would save me time, which matters when I'm on a lunch break.",
                "sample_number": 1
            }
        }


class SSRResult(BaseModel):
    """
    Result of applying Semantic Similarity Rating to a response.

    Contains probability distribution over Likert scale.
    """
    persona_id: str
    concept_id: str
    sample_number: int
    anchor_set_id: int

    # Embedding similarities (raw cosine similarity to each anchor)
    similarities: Dict[int, float] = Field(..., description="Similarity to each rating (1-5)")

    # Probability distribution (normalized similarities)
    probability_distribution: Dict[int, float] = Field(
        ...,
        description="Probability mass function over ratings 1-5"
    )

    # Summary statistics
    mean_rating: float = Field(..., ge=1.0, le=5.0, description="Expected value of distribution")
    mode_rating: int = Field(..., ge=1, le=5, description="Most likely rating")

    # Original response
    response_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "p1",
                "concept_id": "c1",
                "sample_number": 1,
                "anchor_set_id": 0,
                "similarities": {1: 0.62, 2: 0.68, 3: 0.75, 4: 0.89, 5: 0.85},
                "probability_distribution": {1: 0.05, 2: 0.08, 3: 0.15, 4: 0.42, 5: 0.30},
                "mean_rating": 4.08,
                "mode_rating": 4,
                "response_text": "I'd probably subscribe..."
            }
        }


class AggregatedResult(BaseModel):
    """
    Aggregated SSR results for a persona-concept pair.

    Averages across samples and anchor sets.
    """
    persona_id: str
    concept_id: str

    # Averaged across all samples and anchor sets
    avg_probability_distribution: Dict[int, float]
    avg_mean_rating: float = Field(..., ge=1.0, le=5.0)

    # Variability measures
    std_mean_rating: float = Field(..., ge=0.0, description="Standard deviation across samples")

    # Sample responses for qualitative analysis
    sample_responses: List[str] = Field(..., min_items=1, description="All text responses")

    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "p1",
                "concept_id": "c1",
                "avg_probability_distribution": {1: 0.04, 2: 0.07, 3: 0.14, 4: 0.45, 5: 0.30},
                "avg_mean_rating": 4.12,
                "std_mean_rating": 0.08,
                "sample_responses": ["I'd probably subscribe...", "This makes sense for my routine..."]
            }
        }
