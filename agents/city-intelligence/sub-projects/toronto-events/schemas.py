"""
Unified Event data model for Toronto events analysis
"""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    """Unified event model across all sources"""

    # Core identifiers
    id: str = Field(..., description="Unique event ID from source")
    source: Literal["eventbrite", "luma", "meetup"] = Field(..., description="Data source")
    url: str = Field(..., description="Event page URL")

    # Basic info
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    category: Optional[str] = Field(None, description="Event category/type")

    # Time
    start_time: datetime = Field(..., description="Event start time")
    end_time: Optional[datetime] = Field(None, description="Event end time")

    # Location
    location_name: Optional[str] = Field(None, description="Venue name")
    address: Optional[str] = Field(None, description="Full address")
    city: Optional[str] = Field(None, description="City")
    neighborhood: Optional[str] = Field(None, description="Neighborhood (if identifiable)")
    is_online: bool = Field(False, description="Is this an online event?")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")

    # People
    organizer_name: Optional[str] = Field(None, description="Organizer/host name")
    organizer_type: Optional[str] = Field(None, description="Organization, Person, Group")
    attendee_count: Optional[int] = Field(None, description="Number of attendees (if available)")
    capacity: Optional[int] = Field(None, description="Max capacity")

    # Cost
    is_free: bool = Field(True, description="Is event free?")
    price: Optional[float] = Field(None, description="Ticket price (if paid)")
    currency: str = Field("CAD", description="Price currency")
    availability: Optional[str] = Field(None, description="Sold out, available, etc.")

    # Meta
    image_url: Optional[str] = Field(None, description="Event image")
    tags: List[str] = Field(default_factory=list, description="Event tags/keywords")
    extracted_at: datetime = Field(default_factory=datetime.now, description="When we extracted this")


class EventCollection(BaseModel):
    """Collection of events with metadata"""

    events: List[Event] = Field(..., description="List of events")
    total_count: int = Field(..., description="Total events extracted")
    sources: List[str] = Field(..., description="Sources used")
    extracted_at: datetime = Field(default_factory=datetime.now)
    city: str = Field("Toronto", description="City analyzed")
