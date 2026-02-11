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
