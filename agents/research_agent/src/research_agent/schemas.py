"""
Pydantic schemas for the Research Agent.
Single source of truth for data structures.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ResearchInput(BaseModel):
    """Input for research: either text or observation ID."""
    text: Optional[str] = Field(None, description="Direct text observation to research")
    observation_id: Optional[str] = Field(None, description="Supabase observation ID (e.g., 'T042')")

    def validate_input(self) -> bool:
        """Ensure either text or observation_id is provided, not both."""
        if self.text and self.observation_id:
            raise ValueError("Provide either 'text' or 'observation_id', not both")
        if not self.text and not self.observation_id:
            raise ValueError("Must provide either 'text' or 'observation_id'")
        return True


class ResearchOutput(BaseModel):
    """Output from Perplexity research."""
    query: str = Field(..., description="The research query sent to Perplexity")
    findings: str = Field(..., description="Research findings from Perplexity")
    sources: list[str] = Field(default_factory=list, description="Source URLs cited by Perplexity")
    metadata: dict = Field(default_factory=dict, description="Additional metadata (tokens, model, etc.)")
