"""Pydantic models for captured analytics events (single source of truth)."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CapturedRequest(BaseModel):
    """One network request that matched a known analytics vendor."""

    ts: float = Field(..., description="Unix time the request was seen")
    step: str = Field(..., description="Funnel step active when the request fired")
    vendor: str = Field(..., description="Vendor label, e.g. ga4, meta_pixel")
    method: str
    url: str
    frame_url: str = Field("", description="URL of the frame that sent it (iframes included)")
    status: Optional[int] = None
    event_names: list[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict, description="Parsed event properties")
    raw_body: Optional[str] = Field(None, description="Truncated POST body for unparsed vendors")
