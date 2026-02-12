"""
Pydantic schemas for the Cognitive Triage System.
This is the SINGLE SOURCE OF TRUTH for data structures.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ===== ENUMS =====

class ItemType(str, Enum):
    """Types of triage items."""
    TASK = "Task"
    OBSERVATION = "Observation"
    SELF_PERCEPTION = "Self-Perception"
    LEARNING = "Learning"
    META_THINKING = "Meta-Thinking"
    RESEARCH_QUESTION = "Research Question"


# ===== LAYER 1: TRIAGE =====

class TriageItem(BaseModel):
    """A single atomic item from Layer 1 triage."""

    id: str = Field(..., description="Unique identifier (e.g., 'T001', 'T002')")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    raw_context: str = Field(..., min_length=1, description="Verbatim text preserving original voice")
    personal_or_work: str = Field(..., description="Personal | Work")
    domain: str = Field(..., min_length=1, description="Domain/category")
    type: str = Field(..., min_length=1, description="Type: Task | Observation | Self-Perception | Learning | Meta-Thinking | Research Question")
    tags: str = Field(..., min_length=1, description="Comma-separated keywords, lowercase")
    niche_signal: bool = Field(..., description="Maps to behavioral patterns that move markets?")
    publishable: bool = Field(..., description="Could become content?")


# ===== LAYER 2: INSIGHT GENERATION =====

class PatternType(str, Enum):
    """Types of meta-patterns detected across insights."""
    NEW_PATTERN = "new_pattern"  # Emerging theme from 2+ insights
    MULTI_LINK = "multi_link"  # Single insight connects 3+ items
    CLUSTER_GROWTH = "cluster_growth"  # Existing pattern got new evidence
    CONTRADICTION = "contradiction"  # Opposing insights (tension)


class InsightItem(BaseModel):
    """A generated insight from Layer 2 - reframes and names patterns."""

    # Identity
    id: str = Field(..., description="Unique identifier (e.g., 'I001', 'I002')")
    date: str = Field(..., description="Date insight was generated (YYYY-MM-DD)")

    # Core content
    insight_text: str = Field(..., min_length=1, description="The insight - reframes the pattern (1-3 sentences)")

    # Linking
    linked_items: List[str] = Field(..., min_items=1, description="IDs of triage items this connects (e.g., ['T004', 'T054'])")
    related_insights: List[str] = Field(default_factory=list, description="IDs of related insights (cross-batch connections)")

    # Metadata
    tags: List[str] = Field(..., min_items=1, description="Thematic tags (identity-cascade, avoidance-pattern, etc.)")
    domain: str = Field(..., min_length=1, description="Domain (same as Layer 1: identity, product, health, etc.)")

    # Publishability
    publishable_angle: Optional[str] = Field(None, description="Content creation angle if applicable")
    niche_signal: bool = Field(..., description="Is this a behavioral pattern worth sharing?")

    # Quality
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM certainty (0.0-1.0)")


class PatternSignal(BaseModel):
    """Meta-pattern detected across insights."""

    pattern_type: PatternType = Field(..., description="Type of pattern detected")
    description: str = Field(..., min_length=1, description="What the pattern reveals")
    involved_insights: List[str] = Field(..., min_items=1, description="Insight IDs involved")
    involved_items: List[str] = Field(..., min_items=1, description="Triage item IDs involved")
    strength: float = Field(..., ge=0.0, le=1.0, description="How strong is this signal? (0.0-1.0)")


class Layer2Output(BaseModel):
    """Complete output from Layer 2 insight generation."""

    insights: List[InsightItem] = Field(default_factory=list, description="Generated insights")
    patterns: List[PatternSignal] = Field(default_factory=list, description="Detected meta-patterns")
    skipped_items: List[str] = Field(default_factory=list, description="IDs of items that didn't produce insights")
    metadata: dict = Field(default_factory=dict, description="Stats: total_items, insights_generated, etc.")


# ===== INPUT SOURCE =====

class BrainDump(BaseModel):
    """Raw input from user (voice note, journal entry, etc.)."""

    id: str = Field(..., description="Unique source ID")
    created_time: datetime = Field(..., description="When created")
    content: str = Field(..., min_length=1, description="Raw text content")
    source_type: str = Field(default="manual", description="voice_note | journal | manual")


# ===== EVALUATION =====

class ItemEvaluation(BaseModel):
    """Evaluation of a single triage item."""

    item_id: str = Field(..., description="ID of the item being evaluated")
    completeness: int = Field(..., ge=1, le=5, description="Did it extract all meaningful content? (1-5)")
    classification_accuracy: int = Field(..., ge=1, le=5, description="Are type/domain correct? (1-5)")
    granularity: int = Field(..., ge=1, le=5, description="Right level of detail? (1-5)")
    tag_quality: int = Field(..., ge=1, le=5, description="Relevant, specific keywords? (1-5)")
    niche_signal_accuracy: int = Field(..., ge=1, le=5, description="Correct behavioral pattern assessment? (1-5)")
    publishability_accuracy: int = Field(..., ge=1, le=5, description="Correct content potential assessment? (1-5)")
    reasoning: str = Field(..., description="Brief explanation of scores")


class TriageEvaluation(BaseModel):
    """Overall evaluation of a triage run (multiple items)."""

    prompt_version: str = Field(..., description="Identifier for the prompt (e.g., 'v1', 'v2')")
    input_text: str = Field(..., description="Original input text")
    num_items: int = Field(..., description="Number of items extracted")
    item_evaluations: List[ItemEvaluation] = Field(..., description="Per-item evaluations")
    overall_score: float = Field(..., ge=0.0, le=5.0, description="Average score across all dimensions")
    strengths: str = Field(..., description="What this prompt does well")
    weaknesses: str = Field(..., description="What this prompt struggles with")
    recommendation: str = Field(..., description="Keep, revise, or discard")
