"""
Carousel generation module.

Two-stage content creation:
1. Stage 1 (Claude): Pattern-driven draft using author's thinking patterns
2. Stage 2 (ChatGPT): Tighten prose and match voice
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from anthropic import Anthropic
from openai import OpenAI

from .schemas import FrameworkAnalysis, CarouselContent, CarouselSlide, VoiceProfile


def load_voice_profile(profile_path: str = "config/voice_profile.json") -> VoiceProfile:
    """Load voice profile."""
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(f"Voice profile not found: {profile_path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    return VoiceProfile(**data)


def load_author_context(context_path: str = "config/author_context.json") -> Dict[str, Any]:
    """Load author context."""
    path = Path(context_path)
    if not path.exists():
        raise FileNotFoundError(f"Author context not found: {context_path}")

    return json.loads(path.read_text(encoding="utf-8"))


def load_prompt(prompt_name: str, prompts_dir: str = "prompts") -> str:
    """Load prompt template from file."""
    path = Path(prompts_dir) / f"{prompt_name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")

    return path.read_text(encoding="utf-8")


def stage1_draft_with_claude(
    analysis: FrameworkAnalysis,
    author_context: Dict[str, Any],
    carousel_angle: str,
    api_key: str,
    model: str = "claude-sonnet-4-20250514"
) -> Dict[str, Any]:
    """
    Stage 1: Generate pattern-driven draft with Claude.

    Args:
        analysis: Framework analysis
        author_context: Author personal context
        carousel_angle: Which angle to develop (from analysis.carousel_angles)
        api_key: Anthropic API key
        model: Claude model

    Returns:
        Draft carousel as dict
    """
    client = Anthropic(api_key=api_key)

    # Load system prompt
    system_prompt = load_prompt("content_draft_claude_system")

    # Build user prompt
    user_prompt = f"""# Framework Analysis

{analysis.analysis_text}

---

# Key Insights
{chr(10).join(f"• {insight}" for insight in analysis.key_insights)}

---

# Carousel Angle to Develop

{carousel_angle}

---

# Author Context

**Identity:** {', '.join(author_context.get('identity', []))}

**Expertise:** {', '.join(author_context.get('expertise', []))}

**Thinking Patterns:**
{chr(10).join(f"• {p}" for p in author_context.get('thinking_patterns', []))}

**Values:** {', '.join(f"{k} (priority: {v})" for k, v in author_context.get('values', {}).items())}

---

Create a 10-slide carousel draft following the structure:
- Slide 1: Hook (use personal observation or behavioral contradiction)
- Slides 2-9: Body insights
- Slide 10: CTA (reflective question)

Return valid JSON:
{{
  "hook": "hook text",
  "slides": [
    {{"slide_number": 2, "text": "slide 2 text"}},
    {{"slide_number": 3, "text": "slide 3 text"}},
    ...
    {{"slide_number": 9, "text": "slide 9 text"}}
  ],
  "cta": "cta text",
  "hook_pattern_used": "pattern name"
}}

Focus on THINKING and PATTERNS, not polished prose. ChatGPT will tighten later."""

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        temperature=0.4,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract JSON
    content = response.content[0].text

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Extract from markdown wrapper
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
            return json.loads(content)
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
            return json.loads(content)
        else:
            raise ValueError(f"Could not parse JSON from Claude: {content[:200]}")


def stage2_tighten_with_chatgpt(
    draft: Dict[str, Any],
    voice_profile: VoiceProfile,
    author_context: Dict[str, Any],
    api_key: str,
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    Stage 2: Tighten prose and match voice with ChatGPT.

    Args:
        draft: Draft from Stage 1
        voice_profile: Voice patterns
        author_context: Author context
        api_key: OpenAI API key
        model: GPT model

    Returns:
        Tightened carousel as dict
    """
    client = OpenAI(api_key=api_key)

    # Load system prompt
    system_prompt = load_prompt("writing_style_system")

    # Build user prompt with draft
    user_prompt = f"""# Draft Carousel to Tighten

**Hook:**
{draft['hook']}

**Body Slides:**
{chr(10).join(f"Slide {s['slide_number']}: {s['text']}" for s in draft['slides'])}

**CTA:**
{draft['cta']}

---

# Author Voice Reminders

**Communication Style:**
- {chr(10).join(f"• {style}" for style in author_context.get('communication_style', []))}

**What to Avoid:**
- {chr(10).join(f"• {avoid}" for avoid in author_context.get('what_to_avoid', []))}

---

Tighten this carousel:
1. Shorten sentences (avg 3-6 words)
2. Use author's voice (I/you pronouns, specific details, no jargon)
3. Apply hook pattern: {draft.get('hook_pattern_used', 'personal_observation')}
4. Keep the same 10-slide structure
5. Match the tone markers from voice profile

Return valid JSON with same structure:
{{
  "hook": "tightened hook",
  "slides": [
    {{"slide_number": 2, "text": "tightened slide 2"}},
    ...
  ],
  "cta": "tightened cta",
  "hook_pattern_used": "{draft.get('hook_pattern_used', 'personal_observation')}"
}}"""

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return json.loads(response.choices[0].message.content)


def generate_carousel(
    analysis: FrameworkAnalysis,
    carousel_angle: str,
    product_name: str,
    voice_profile_path: str = "config/voice_profile.json",
    author_context_path: str = "config/author_context.json",
    output_path: Optional[str] = None
) -> CarouselContent:
    """
    Main function: Generate carousel from analysis.

    Args:
        analysis: Framework analysis
        carousel_angle: Which angle to develop
        product_name: Product name for metadata
        voice_profile_path: Path to voice profile
        author_context_path: Path to author context
        output_path: Optional path to save carousel JSON

    Returns:
        CarouselContent object (validated)
    """
    # Load API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not anthropic_key or not openai_key:
        raise ValueError("ANTHROPIC_API_KEY and OPENAI_API_KEY required")

    # Load context
    print("\n📚 Loading voice profile and author context...")
    voice_profile = load_voice_profile(voice_profile_path)
    author_context = load_author_context(author_context_path)
    print("   ✓ Context loaded")

    # Stage 1: Claude draft
    print("\n🤖 Stage 1: Generating pattern-driven draft with Claude...")
    draft = stage1_draft_with_claude(
        analysis=analysis,
        author_context=author_context,
        carousel_angle=carousel_angle,
        api_key=anthropic_key
    )
    print("   ✓ Draft generated")

    # Stage 2: ChatGPT tightening
    print("\n✍️  Stage 2: Tightening prose with ChatGPT...")
    final = stage2_tighten_with_chatgpt(
        draft=draft,
        voice_profile=voice_profile,
        author_context=author_context,
        api_key=openai_key
    )
    print("   ✓ Prose tightened")

    # Build CarouselContent
    carousel_data = {
        "topic": product_name,
        "hook": final["hook"],
        "slides": [
            CarouselSlide(
                slide_number=s["slide_number"],
                text=s["text"],
                text_length=len(s["text"])
            ) for s in final["slides"]
        ],
        "cta": final["cta"],
        "hook_pattern_used": final.get("hook_pattern_used"),
        "voice_profile_version": voice_profile.version,
        "total_slides": 1 + len(final["slides"]) + 1  # hook + body + cta
    }

    # Validate
    print("\n✓ Validating carousel structure...")
    carousel = CarouselContent(**carousel_data)

    # Save if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(carousel.model_dump(), indent=2, default=str),
            encoding="utf-8"
        )
        print(f"\n💾 Saved carousel to: {output_path}")

    return carousel


def display_carousel(carousel: CarouselContent):
    """Display carousel for review."""
    print("\n" + "="*70)
    print("📱 CAROUSEL PREVIEW")
    print("="*70)

    print(f"\n🎯 Topic: {carousel.topic}")
    print(f"📊 Total Slides: {carousel.total_slides}")
    print(f"🎨 Hook Pattern: {carousel.hook_pattern_used}")
    print(f"🎤 Voice Match Confidence: {carousel.voice_match_confidence or 'N/A'}")

    print("\n" + "-"*70)
    print("SLIDE 1 (HOOK)")
    print("-"*70)
    print(carousel.hook)
    print(f"\n[{len(carousel.hook)} characters]")

    for slide in carousel.slides:
        print("\n" + "-"*70)
        print(f"SLIDE {slide.slide_number}")
        print("-"*70)
        print(slide.text)
        print(f"\n[{slide.text_length} characters]")

    print("\n" + "-"*70)
    print(f"SLIDE {carousel.total_slides} (CTA)")
    print("-"*70)
    print(carousel.cta)
    print(f"\n[{len(carousel.cta)} characters]")

    print("\n" + "="*70)
