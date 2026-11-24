"""Pydantic models: single source of truth for everything the analyzer produces."""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FontStyle(str, Enum):
    SANS = "sans"
    SERIF = "serif"
    SCRIPT = "script"
    HANDWRITTEN = "handwritten"
    DISPLAY = "display"
    MONO = "mono"
    OTHER = "other"


class TextPosition(str, Enum):
    TOP = "top"
    UPPER_THIRD = "upper_third"
    CENTER = "center"
    LOWER_THIRD = "lower_third"
    BOTTOM = "bottom"
    OTHER = "other"


class TextOverlay(BaseModel):
    """One piece of on-screen text, described so an editor can recreate it."""
    text: str
    font_style: FontStyle
    font_description: str = Field(..., description="Closest known font + traits, e.g. 'Bodoni-like high-contrast serif'")
    weight: str = Field(..., description="light / regular / bold / black")
    case: str = Field(..., description="upper / lower / title / mixed")
    color_hex: str
    position: TextPosition
    relative_size: str = Field(..., description="small / medium / large / huge (share of frame width)")
    background: str = Field(..., description="none / box / highlight / outline / shadow / blur")
    animation: str = Field(..., description="static / fade / pop / typewriter / slide / word-by-word / unknown")


class ShotAnalysis(BaseModel):
    """LLM reading of one shot (from 3 frames)."""
    shot_type: str = Field(..., description="e.g. close-up, wide, macro, POV, screen-recording, title-card")
    subject: str
    camera_motion: str = Field(..., description="static / pan / tilt / push-in / handheld / zoom / unknown")
    lighting_and_grade: str
    transition_in: str = Field(..., description="hard cut / crossfade / whip / zoom / flash / glitch / none / unknown")
    effects: List[str] = Field(default_factory=list, description="grain, vignette, speed ramp, overlays, stickers...")
    text_overlays: List[TextOverlay] = Field(default_factory=list)
    editor_notes: str = Field(..., description="What an editor must do to recreate this shot")


class Shot(BaseModel):
    """One shot: deterministic facts plus the LLM reading."""
    index: int
    start: float
    end: float
    duration: float
    palette: List[str] = Field(default_factory=list, description="Dominant colors as hex")
    ocr_text: str = ""
    frames: List[str] = Field(default_factory=list)
    analysis: Optional[ShotAnalysis] = None


class AudioInfo(BaseModel):
    transcript: str = ""
    words: List[dict] = Field(default_factory=list)
    mean_volume_db: Optional[float] = None
    max_volume_db: Optional[float] = None
    silent_segments: List[List[float]] = Field(default_factory=list)


class Pacing(BaseModel):
    shot_count: int
    avg_shot_s: float
    median_shot_s: float
    shortest_s: float
    longest_s: float
    cuts_per_minute: float


class VideoStyleSpec(BaseModel):
    """Final artifact: what to feed back when editing a video in this style."""
    source: str
    duration_s: float
    resolution: str
    fps: float
    pacing: Pacing
    palette: List[str]
    shots: List[Shot]
    audio: AudioInfo
    style_summary: str = ""
