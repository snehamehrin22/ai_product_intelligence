"""
Pydantic schemas for the notes agent.
This is the SINGLE SOURCE OF TRUTH for data structures.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CognitiveBlock(BaseModel):
    """A single cognitive block from a journal entry."""

    block_id: str = Field(..., description="Unique block identifier (e.g., 'b1', 'b2')")
    block_name: str = Field(..., min_length=2, max_length=50, description="2-6 word human-readable name")
    block_text: str = Field(..., min_length=1, description="The actual text content of this block")


class BlockSplitResponse(BaseModel):
    """Response from the block splitter LLM."""

    blocks: List[CognitiveBlock] = Field(..., min_items=1, description="List of cognitive blocks")


class BlockClassification(BaseModel):
    """Psychological classification of a cognitive block."""

    block_id: str = Field(..., description="Block identifier")
    block_text: str = Field(..., min_length=1, description="Block text")
    themes: List[str] = Field(..., min_items=3, max_items=8, description="3-8 keyword themes")
    core_emotion: str = Field(..., min_length=1, description="Primary emotion detected")
    nervous_system_state: str = Field(..., min_length=1, description="Physiological state")
    behavioral_response: str = Field(..., min_length=1, description="Action pattern")
    fear_underneath: Optional[str] = Field(None, description="Unstated fears or blockers")
    self_concept_gap: Optional[str] = Field(None, description="Aspiration vs reality mismatch")
    action_signal: str = Field(..., min_length=1, description="Directional impulse")
    action_note: Optional[str] = Field(None, description="Concrete action suggestion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM certainty (0-1)")


class ClassifiedBlock(BaseModel):
    """A cognitive block with its classification."""

    block: CognitiveBlock
    classification: BlockClassification


class NotionEntry(BaseModel):
    """A journal entry from Notion."""

    id: str = Field(..., description="Notion page ID")
    created_time: datetime = Field(..., description="When the entry was created")
    content: str = Field(..., min_length=1, description="Raw journal text content")
