"""
Voice profile analysis and generation.

Extracts writing style patterns from training carousels and creates
a voice profile that can be used to constrain content generation.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from anthropic import Anthropic
from dotenv import load_dotenv

from .schemas import VoiceProfile, HookPattern, ToneMarker

load_dotenv()


def load_prompt(prompt_name: str) -> str:
    """Load prompt from prompts/ folder."""
    project_root = Path(__file__).parent.parent.parent
    prompt_path = project_root / "prompts" / f"{prompt_name}.txt"
    return prompt_path.read_text(encoding="utf-8")


def load_training_carousels(training_dir: str) -> List[Dict[str, str]]:
    """
    Load carousel text samples from training directory.

    Expected format: One file per carousel, named carousel_01.txt, carousel_02.txt, etc.
    Each file contains the full carousel text (hook + body + CTA).

    Returns list of dicts with 'id' and 'content' keys.
    """
    training_path = Path(training_dir)

    if not training_path.exists():
        raise FileNotFoundError(
            f"Training directory not found: {training_dir}\n"
            f"Create it and add your carousel samples."
        )

    carousel_files = sorted(training_path.glob("carousel_*.txt"))

    if len(carousel_files) < 3:
        raise ValueError(
            f"Need at least 3 carousel samples, found {len(carousel_files)}\n"
            f"Add more samples to {training_dir}"
        )

    carousels = []
    for file_path in carousel_files:
        carousel_id = file_path.stem  # e.g., "carousel_01"
        content = file_path.read_text(encoding="utf-8").strip()

        if len(content) < 100:
            print(f"Warning: {file_path.name} seems too short ({len(content)} chars)")
            continue

        carousels.append({
            "id": carousel_id,
            "content": content
        })

    return carousels


def analyze_voice_with_claude(
    carousels: List[Dict[str, str]],
    api_key: str
) -> Dict[str, Any]:
    """
    Use Claude to analyze carousel samples and extract voice patterns.

    Returns raw analysis dict that will be validated into VoiceProfile schema.
    """
    client = Anthropic(api_key=api_key)

    system_prompt = load_prompt("voice_analysis_system")

    # Prepare user message with all carousel samples
    user_message = "Analyze these carousel samples and extract the author's voice patterns:\n\n"

    for i, carousel in enumerate(carousels, 1):
        user_message += f"=== CAROUSEL SAMPLE {i} ({carousel['id']}) ===\n"
        user_message += carousel['content']
        user_message += "\n\n"

    user_message += (
        "Analyze all samples above and provide your complete analysis as JSON. "
        "Look for patterns that repeat across multiple samples."
    )

    print(f"Analyzing {len(carousels)} carousel samples with Claude...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        temperature=0.3,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    # Extract JSON from response
    response_text = response.content[0].text

    # Claude may wrap JSON in markdown code blocks
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.rfind("```")
        json_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.rfind("```")
        json_text = response_text[json_start:json_end].strip()
    else:
        # Try to find JSON object
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            raise ValueError("Could not find JSON in Claude's response")
        json_text = response_text[json_start:json_end]

    analysis = json.loads(json_text)

    print("✓ Voice analysis complete")

    return analysis


def convert_to_voice_profile(
    analysis: Dict[str, Any],
    carousel_ids: List[str]
) -> VoiceProfile:
    """
    Convert raw analysis dict to validated VoiceProfile schema.

    This ensures all required fields are present and properly typed.
    """
    # Convert hook patterns
    hook_patterns = [
        HookPattern(
            pattern_type=hp.get("pattern_type", "bold_statement"),
            example=hp.get("example", ""),
            frequency=hp.get("frequency", 1)
        )
        for hp in analysis.get("hook_patterns", [])
    ]

    # Convert tone markers
    tone_markers = [
        ToneMarker(
            marker_type=tm.get("marker_type", "vocabulary"),
            description=tm.get("description", ""),
            examples=tm.get("examples", [])
        )
        for tm in analysis.get("tone_markers", [])
    ]

    # Extract structure info
    structure = analysis.get("structure", {})

    # Create voice profile
    profile = VoiceProfile(
        version="1.0",
        created_at=datetime.now(),
        hook_patterns=hook_patterns,
        typical_slide_count=structure.get("typical_slide_count", 10),
        cta_style=structure.get("cta_style", "Direct call to action"),
        tone_markers=tone_markers,
        training_carousel_count=len(carousel_ids),
        training_carousel_ids=carousel_ids
    )

    return profile


def generate_writing_style_prompt(profile: VoiceProfile) -> str:
    """
    Generate a system prompt for ChatGPT that encodes the voice profile.

    This prompt will be used during content generation to match the voice.
    """
    prompt = "You are writing carousel content in a specific author's voice. Follow these style rules:\n\n"

    # Hook patterns
    prompt += "## Hook Patterns\n"
    prompt += "Use these hook types (in order of frequency):\n"
    for hp in sorted(profile.hook_patterns, key=lambda x: x.frequency, reverse=True):
        prompt += f"- {hp.pattern_type.replace('_', ' ').title()} (example: \"{hp.example}\")\n"
    prompt += "\n"

    # Structure
    prompt += "## Structure\n"
    prompt += f"- Typical carousel length: {profile.typical_slide_count} slides (including hook and CTA)\n"
    prompt += f"- CTA style: {profile.cta_style}\n\n"

    # Tone markers
    prompt += "## Tone & Style\n"
    for tm in profile.tone_markers:
        prompt += f"- {tm.marker_type.replace('_', ' ').title()}: {tm.description}\n"
        if tm.examples:
            examples_str = ', '.join(f'"{ex}"' for ex in tm.examples[:3])
            prompt += f"  Examples: {examples_str}\n"
    prompt += "\n"

    prompt += "## Rules\n"
    prompt += "- Match this voice exactly. Do not add generic AI phrases.\n"
    prompt += "- Maintain the same pronoun usage, sentence structure, and vocabulary level.\n"
    prompt += "- Use the hook patterns and CTA style shown above.\n"
    prompt += "- Keep the typical slide count and structure.\n"

    return prompt


def save_voice_profile(
    profile: VoiceProfile,
    output_path: str,
    analysis: Dict[str, Any]
) -> None:
    """
    Save voice profile to config directory.

    Saves both the validated schema and the raw analysis for reference.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save validated profile
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(profile.model_dump(mode='json'), f, indent=2, default=str)

    print(f"✓ Voice profile saved: {output_file}")

    # Save raw analysis for reference
    analysis_file = output_file.parent / "voice_analysis_raw.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    print(f"✓ Raw analysis saved: {analysis_file}")

    # Generate and save writing style prompt
    style_prompt = generate_writing_style_prompt(profile)
    prompt_file = output_file.parent.parent / "prompts" / "writing_style_system.txt"
    prompt_file.write_text(style_prompt, encoding='utf-8')

    print(f"✓ Writing style prompt saved: {prompt_file}")


def build_voice_profile(
    training_dir: str = "data/training_carousels",
    output_path: str = "config/voice_profile.json"
) -> VoiceProfile:
    """
    Main function to build voice profile from training carousels.

    Steps:
    1. Load carousel samples from training directory
    2. Analyze with Claude to extract patterns
    3. Convert to validated VoiceProfile schema
    4. Generate writing style prompt for ChatGPT
    5. Save everything

    Returns the validated VoiceProfile.
    """
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment.\n"
            "Add it to your .env file."
        )

    # Load training carousels
    print("Loading training carousels...")
    carousels = load_training_carousels(training_dir)
    print(f"✓ Loaded {len(carousels)} carousel samples")

    # Analyze with Claude
    analysis = analyze_voice_with_claude(carousels, api_key)

    # Convert to schema
    print("Converting to voice profile schema...")
    carousel_ids = [c["id"] for c in carousels]
    profile = convert_to_voice_profile(analysis, carousel_ids)
    print("✓ Voice profile validated")

    # Save everything
    save_voice_profile(profile, output_path, analysis)

    print(f"\n✓ Voice profile build complete!")
    print(f"  - Training samples: {len(carousels)}")
    print(f"  - Hook patterns: {len(profile.hook_patterns)}")
    print(f"  - Tone markers: {len(profile.tone_markers)}")
    print(f"  - Typical slides: {profile.typical_slide_count}")

    return profile
