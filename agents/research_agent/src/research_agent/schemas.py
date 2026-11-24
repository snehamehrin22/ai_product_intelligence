"""Pydantic schemas for the research-angle pipeline (single source of truth).

Stage files written by the Claude Code subagents are validated against these
before the next stage runs, so a malformed or ungrounded stage fails loudly.
"""
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, HttpUrl, model_validator


class Status(str, Enum):
    """How well-established a claim is."""
    ESTABLISHED = "established"
    DISPUTED = "disputed"
    SPECULATIVE = "speculative"


class Note(BaseModel):
    """One sourced claim from Stage 1 research."""
    note_id: str = Field(..., pattern=r"^n\d+$")
    area: str = Field(..., min_length=2, description="e.g. origins, economics, contradictions")
    claim: str = Field(..., min_length=10)
    status: Status
    source_url: HttpUrl


class ResearchNotes(BaseModel):
    """Stage 1 output."""
    observation: str = Field(..., min_length=5)
    notes: List[Note] = Field(..., min_length=8)


class Finding(BaseModel):
    """A surprising, source-backed discovery (Stage 2)."""
    finding_id: str = Field(..., pattern=r"^f\d+$")
    summary: str = Field(..., min_length=20)
    why_interesting: str = Field(..., min_length=10)
    note_ids: List[str] = Field(..., min_length=1)
    source_url: HttpUrl


class Findings(BaseModel):
    """Stage 2 output: 5-8 findings."""
    findings: List[Finding] = Field(..., min_length=5, max_length=8)


class Angle(BaseModel):
    """One research angle (Stage 3)."""
    angle: str = Field(..., min_length=3, max_length=60)
    research_question: str = Field(..., min_length=15)
    hypothesis: str = Field(..., min_length=15)
    preliminary_evidence: str = Field(..., min_length=15)
    finding_id: str = Field(..., pattern=r"^f\d+$")
    speculative: bool
    challenges_assumption: bool = Field(
        ..., description="True if the angle contradicts the user's original framing"
    )


class Angles(BaseModel):
    """Stage 3 output: 10-15 angles."""
    angles: List[Angle] = Field(..., min_length=10, max_length=15)

    @model_validator(mode="after")
    def some_challenge_assumptions(self) -> "Angles":
        """Prompt requires some angles to challenge the original assumption."""
        if not any(a.challenges_assumption for a in self.angles):
            raise ValueError("At least one angle must challenge the original assumption")
        return self
