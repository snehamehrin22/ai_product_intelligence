"""Pydantic models: the single source of truth for what valid data looks like."""

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# Instagram usernames: letters, numbers, periods, underscores, up to 30 chars.
# We store them lowercase because Instagram treats them case-insensitively.
HANDLE_PATTERN = re.compile(r"^[a-z0-9._]{1,30}$")


class Creator(BaseModel):
    """One Instagram creator in the seed list."""

    handle: str = Field(..., description="Instagram username, lowercase, no '@'")
    source: str = Field(..., description="Where the creator came from: 'notion' or 'manual'")
    notion_category: str = Field("", description="Notion categories joined with '|'")
    notes: str = ""

    @field_validator("handle")
    @classmethod
    def handle_must_be_clean(cls, value: str) -> str:
        """Reject handles that normalize_handle() should have cleaned already.

        Strict on purpose: cleaning happens once, at import time. If a dirty
        handle reaches this model, something upstream skipped that step.
        """
        if not HANDLE_PATTERN.match(value):
            raise ValueError(f"invalid handle {value!r}: expected lowercase [a-z0-9._], 1-30 chars")
        return value

    @field_validator("source")
    @classmethod
    def source_must_be_known(cls, value: str) -> str:
        """Limit source to the two origins we have."""
        if value not in {"notion", "manual"}:
            raise ValueError(f"unknown source {value!r}")
        return value


class CreatorList(BaseModel):
    """The whole seed list; enforces uniqueness across creators."""

    creators: List[Creator]

    @field_validator("creators")
    @classmethod
    def handles_must_be_unique(cls, value: List[Creator]) -> List[Creator]:
        """A duplicate would be scraped (and paid for) twice."""
        seen = set()
        for creator in value:
            if creator.handle in seen:
                raise ValueError(f"duplicate handle {creator.handle!r}")
            seen.add(creator.handle)
        return value


class AccountStatus(BaseModel):
    """What we need to know about the Apify account before spending money."""

    username: str
    plan: str
    tier: str
    monthly_cap_usd: float
    spent_usd: float
    price_per_reel_usd: float
    price_per_profile_usd: float
    start_fee_usd: float

    @property
    def remaining_usd(self) -> float:
        """Credit left this billing month."""
        return round(self.monthly_cap_usd - self.spent_usd, 4)


class Reel(BaseModel):
    """One reel as returned by the Apify reel scraper, reduced to what we use.

    Views are required: the first analyzer silently wrote empty views because it
    read a field Apify leaves null. A reel without views can't be ranked, so it
    must fail validation, not pass through as a blank.
    """

    shortcode: str
    url: str
    username: str
    views: int = Field(..., ge=0, description="videoPlayCount (videoViewCount is always null)")
    likes: Optional[int] = None
    comments: Optional[int] = None
    duration_seconds: Optional[float] = None
    posted_at: str
    caption: str = ""
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    product_type: Optional[str] = None
