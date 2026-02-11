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

class Insight(BaseModel):
    """An extracted insight from Layer 2."""

    insight_id: str = Field(..., description="Unique identifier (e.g., 'ins1')")
    insight_text: str = Field(..., min_length=1, description="The extracted pattern/reframe")
    mechanism: str = Field(..., min_length=1, description="Behavioral mechanism at play")
    source_item_ids: List[str] = Field(..., min_items=1, description="Links to TriageItem IDs")
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM certainty (0-1)")


class InsightResponse(BaseModel):
    """Response from Layer 2 insight LLM."""

    insights: List[Insight] = Field(default_factory=list, description="List of extracted insights")


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
