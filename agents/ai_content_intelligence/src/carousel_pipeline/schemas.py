"""
Pydantic schemas for carousel content pipeline.

These models define the single source of truth for all data structures
and enforce validation throughout the pipeline.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Any
from datetime import datetime


# ============================================================================
# Voice Profile Schemas
# ============================================================================

class HookPattern(BaseModel):
    """A hook pattern extracted from training carousels."""
    pattern_type: str = Field(..., min_length=3, description="Hook pattern type")
    example: str = Field(..., min_length=5, description="Example hook from training data")
    frequency: int = Field(..., ge=1, description="How many times this pattern appeared")


class ToneMarker(BaseModel):
    """Tone and style markers for voice matching."""
    marker_type: str = Field(..., min_length=3, description="Tone marker type")
    description: str = Field(..., min_length=3)
    examples: List[str] = Field(..., min_items=1)


class VoiceProfile(BaseModel):
    """Complete voice profile extracted from training carousels."""
    version: str = Field(default="1.0", description="Voice profile version")
    created_at: datetime = Field(default_factory=datetime.now)

    # Structure patterns
    hook_patterns: List[HookPattern] = Field(..., min_items=1)
    typical_slide_count: int = Field(..., ge=5, le=20, description="Typical number of slides")
    cta_style: str = Field(..., min_length=10, description="Call-to-action style description")

    # Tone markers
    tone_markers: List[ToneMarker] = Field(..., min_items=3)

    # Training metadata
    training_carousel_count: int = Field(..., ge=3, description="Number of carousels used for training")
    training_carousel_ids: List[str] = Field(..., min_items=3)


# ============================================================================
# Research Schemas
# ============================================================================

class ResearchLens(BaseModel):
    """A research lens for multi-angle investigation."""
    lens_name: Literal["anthropological", "psychological", "historical", "economic", "sociological", "technological"]
    prompt_template: str = Field(..., min_length=20, description="Perplexity prompt template for this lens")


class ResearchSource(BaseModel):
    """A source cited in research."""
    url: str
    title: str
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ResearchInsight(BaseModel):
    """A single insight from research."""
    lens: str = Field(..., description="Which lens produced this insight")
    insight: str = Field(..., min_length=20)
    sources: List[ResearchSource] = Field(default_factory=list)


class ResearchReport(BaseModel):
    """Complete research report for a topic."""
    topic: str = Field(..., min_length=5)
    lenses_used: List[str] = Field(..., min_items=1)
    created_at: datetime = Field(default_factory=datetime.now)

    # Research content
    insights: List[ResearchInsight] = Field(..., min_items=1)
    key_themes: List[str] = Field(..., min_items=1, description="Cross-lens patterns")
    open_questions: List[str] = Field(default_factory=list)

    # Metadata
    total_sources: int = Field(..., ge=1)
    research_duration_seconds: Optional[float] = None


# ============================================================================
# Content Generation Schemas
# ============================================================================

class CarouselSlide(BaseModel):
    """A single slide in a carousel."""
    slide_number: int = Field(..., ge=1, description="Slide position (1-indexed)")
    text: str = Field(..., min_length=5, max_length=500, description="Slide text content")
    text_length: int = Field(..., ge=5, description="Character count for layout validation")

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-calculate text length
        if 'text_length' not in data:
            self.text_length = len(self.text)


# ============================================================================
# XML Carousel Generation Schemas (Direct Generation)
# ============================================================================

class XMLCarouselSlide(BaseModel):
    """A single slide in XML carousel format."""
    index: int = Field(..., ge=1, description="Slide index (1-indexed)")
    title: Optional[str] = Field(None, description="Optional slide title")
    text_lines: List[str] = Field(..., min_items=1, max_items=5, description="1-3 short lines per slide")

    @property
    def full_text(self) -> str:
        """Get full slide text as single string."""
        return "\n".join(self.text_lines)


class DirectCarouselOutput(BaseModel):
    """Carousel output from direct XML generation (no framework analysis step)."""
    title: str = Field(..., min_length=5, description="Carousel title")
    pillar: str = Field(..., description="Pillar ID (e.g., 'pillar_01')")
    slides: List[XMLCarouselSlide] = Field(..., min_items=5, max_items=15)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    source_research: Optional[str] = Field(None, description="Path to source research file")
    framework_used: Optional[str] = Field(None, description="Framework file used")
    total_slides: int = Field(..., ge=5, le=15)

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-calculate total slides
        if 'total_slides' not in data:
            self.total_slides = len(self.slides)


class CarouselContent(BaseModel):
    """Complete carousel content structure."""
    topic: str = Field(..., min_length=5)
    created_at: datetime = Field(default_factory=datetime.now)

    # Content
    hook: str = Field(..., min_length=10, max_length=150, description="Hook slide content")
    slides: List[CarouselSlide] = Field(..., min_items=5, max_items=20)
    cta: str = Field(..., min_length=10, max_length=150, description="Call-to-action slide")

    # Metadata
    research_source: Optional[str] = Field(None, description="Path to research report used")
    voice_profile_version: str = Field(default="1.0")
    voice_match_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Generation details
    hook_pattern_used: Optional[str] = None
    total_slides: int = Field(..., ge=7, le=22, description="Hook + body + CTA")

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-calculate total slides
        if 'total_slides' not in data:
            self.total_slides = 1 + len(self.slides) + 1  # hook + body + cta


# ============================================================================
# Design Schemas
# ============================================================================

class BrandColors(BaseModel):
    """Brand color palette."""
    primary: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    accent: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    text: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")


class TypographySpec(BaseModel):
    """Typography specifications."""
    font_family: str = Field(..., min_length=3)
    hook_size: int = Field(..., ge=20, le=100, description="Hook slide font size in pt")
    body_size: int = Field(..., ge=16, le=60, description="Body slide font size in pt")
    cta_size: int = Field(..., ge=18, le=80, description="CTA slide font size in pt")
    line_height: float = Field(..., ge=1.0, le=2.0, description="Line height multiplier")
    font_weight: Literal["light", "regular", "medium", "semibold", "bold"] = "regular"


class LayoutSpec(BaseModel):
    """Layout specifications for carousel template."""
    template_name: Literal["A", "B"]
    description: str = Field(..., min_length=10)

    # Spacing
    padding_horizontal: int = Field(..., ge=20, le=150, description="Horizontal padding in px")
    padding_vertical: int = Field(..., ge=20, le=150, description="Vertical padding in px")

    # Layout type
    layout_type: Literal["text_heavy", "visual_heavy", "balanced"]
    icon_usage: bool = Field(default=False, description="Whether this template uses icons")
    icon_style: Optional[Literal["outline", "filled", "none"]] = "none"


class DesignTemplate(BaseModel):
    """Complete design template specification."""
    template_id: Literal["A", "B"]
    name: str = Field(..., min_length=3)

    # Design specs
    colors: BrandColors
    typography: TypographySpec
    layout: LayoutSpec

    # Canvas
    canvas_width: int = Field(default=1080, ge=1000, le=2000)
    canvas_height: int = Field(default=1080, ge=1000, le=2000)

    # Metadata
    tested: bool = Field(default=False, description="Has this template been tested?")
    success_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Generation success rate")


class GeneratedCarousel(BaseModel):
    """Metadata for a generated carousel with design."""
    content_id: str = Field(..., description="Reference to CarouselContent")
    template_used: Literal["A", "B"]
    created_at: datetime = Field(default_factory=datetime.now)

    # Output paths
    output_folder: str = Field(..., min_length=5)
    slide_files: List[str] = Field(..., min_items=7, description="Paths to slide PNG files")
    thumbnail_file: str = Field(..., description="Path to thumbnail (slide 1)")

    # Generation metadata
    generation_success: bool = Field(default=True)
    generation_errors: List[str] = Field(default_factory=list)
    regeneration_count: int = Field(default=0, ge=0, description="How many times regenerated")


# ============================================================================
# Feedback and Learning Schemas
# ============================================================================

class StepFeedback(BaseModel):
    """Feedback for a single pipeline step."""
    step_name: str = Field(..., description="pillar_matching, framework_analysis, carousel_draft, or final_tightening")
    timestamp: datetime = Field(default_factory=datetime.now)
    quality_rating: int = Field(..., ge=1, le=5, description="1-5 quality rating")
    approved: bool = Field(..., description="Did user approve this step?")
    issues: List[str] = Field(default_factory=list, description="List of issues identified")
    what_was_wrong: Optional[str] = Field(None, description="What was incorrect")
    what_was_missing: Optional[str] = Field(None, description="What was missing")
    manual_edits_made: Optional[str] = Field(None, description="Edits user made manually")
    notes: Optional[str] = Field(None, description="Additional notes")


class CarouselFeedback(BaseModel):
    """Complete feedback for one carousel creation session."""
    product_name: str = Field(..., min_length=2)
    research_file: str = Field(..., description="Path to research file")
    pillar_used: str = Field(..., description="Content pillar applied")

    # Feedback per step
    pillar_matching_feedback: Optional[StepFeedback] = None
    framework_analysis_feedback: Optional[StepFeedback] = None
    carousel_draft_feedback: Optional[StepFeedback] = None
    final_tightening_feedback: Optional[StepFeedback] = None

    # Overall metrics
    published: bool = Field(default=False)
    time_to_complete: Optional[float] = Field(None, description="Minutes to complete")
    total_iterations: int = Field(default=1, description="How many times regenerated")
    success_rating: int = Field(..., ge=1, le=5, description="Overall success 1-5")

    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ContentPillar(BaseModel):
    """Definition of a content pillar/theme."""
    pillar_id: str = Field(..., description="Unique ID like 'growth_loops_are_changing'")
    name: str = Field(..., min_length=3)
    thesis: str = Field(..., min_length=20, description="Core thesis of this pillar")
    shifts: List[str] = Field(..., min_items=1, description="Key behavioral shifts")
    framework_file: str = Field(..., description="Path to framework template")
    carousel_structure: str = Field(..., description="Carousel format to use")
    keywords: List[str] = Field(default_factory=list, description="Keywords for auto-matching")


class PillarMatch(BaseModel):
    """Result of matching research to a content pillar."""
    pillar_id: str
    pillar_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=20)
    shifts_identified: List[str] = Field(..., description="Which shifts from pillar apply")
    alternative_matches: List[Dict[str, Any]] = Field(default_factory=list)


class FrameworkAnalysis(BaseModel):
    """Result of applying framework to research."""
    pillar_id: str
    framework_used: str
    key_insights: List[str] = Field(..., min_items=1)
    growth_loops_identified: Optional[List[str]] = None
    shifts_mapped: Dict[str, str] = Field(default_factory=dict)
    gaps_identified: List[str] = Field(default_factory=list)
    carousel_angles: List[str] = Field(..., min_items=1, description="Potential carousel angles")
    analysis_text: str = Field(..., min_length=100, description="Full analysis")


# ============================================================================
# Pipeline Orchestration Schemas
# ============================================================================

class PipelineConfig(BaseModel):
    """Configuration for end-to-end pipeline run."""
    topic: str = Field(..., min_length=5)

    # Research config
    research_lenses: List[str] = Field(default=["anthropological", "psychological", "historical"])
    skip_research: bool = Field(default=False)
    existing_research_path: Optional[str] = None

    # Content config
    voice_profile_path: str = Field(default="config/voice_profile.json")
    content_angle: Optional[str] = Field(None, description="Optional specific angle/hook")

    # Design config
    template_choice: Literal["A", "B", "auto"] = "auto"

    # Output config
    output_base_dir: str = Field(default="data/generated_carousels")
    save_intermediates: bool = Field(default=True, description="Save research and content JSON")


class PipelineResult(BaseModel):
    """Result from complete pipeline run."""
    topic: str
    started_at: datetime
    completed_at: datetime
    total_duration_seconds: float

    # Stage results
    research_completed: bool
    research_path: Optional[str] = None

    content_completed: bool
    content_path: Optional[str] = None

    design_completed: bool
    carousel_folder: Optional[str] = None

    # Summary
    success: bool
    errors: List[str] = Field(default_factory=list)
    manual_edits_needed: Optional[int] = Field(None, description="Estimated edits needed")

    # Metrics
    voice_match_confidence: Optional[float] = None
    design_generation_attempts: int = Field(default=1)
