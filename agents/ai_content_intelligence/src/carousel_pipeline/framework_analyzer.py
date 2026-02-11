"""
Framework analysis module.

Takes research markdown and applies a content pillar framework
to generate structured analysis ready for carousel creation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from anthropic import Anthropic

from .schemas import FrameworkAnalysis


def load_research(research_path: str) -> str:
    """
    Load research markdown from Obsidian.

    Args:
        research_path: Path to research markdown file

    Returns:
        Research content as string

    Raises:
        FileNotFoundError: If research file doesn't exist
    """
    path = Path(research_path)
    if not path.exists():
        raise FileNotFoundError(f"Research file not found: {research_path}")

    return path.read_text(encoding="utf-8")


def load_framework(framework_path: str) -> str:
    """
    Load framework template.

    Args:
        framework_path: Path to framework markdown

    Returns:
        Framework template as string
    """
    path = Path(framework_path)
    if not path.exists():
        raise FileNotFoundError(f"Framework not found: {framework_path}")

    return path.read_text(encoding="utf-8")


def apply_framework_with_claude(
    research: str,
    framework: str,
    pillar_name: str,
    api_key: str,
    model: str = "claude-sonnet-4-20250514"
) -> Dict[str, Any]:
    """
    Apply framework to research using Claude.

    Args:
        research: Research content
        framework: Framework template
        pillar_name: Name of content pillar
        api_key: Anthropic API key
        model: Claude model to use

    Returns:
        Structured analysis as dict
    """
    client = Anthropic(api_key=api_key)

    system_prompt = f"""You are analyzing product research through the "{pillar_name}" framework.

Your task:
1. Read the research carefully
2. Apply the framework structure provided
3. Return a complete, structured analysis following the framework template
4. Focus on behavioral evidence and specific patterns
5. Generate actionable carousel angles

Return your analysis as valid JSON with this structure:
{{
  "key_insights": ["insight 1", "insight 2", ...],
  "growth_loops_identified": ["loop 1", "loop 2", ...],
  "shifts_mapped": {{"shift_name": "how it applies to this product"}},
  "gaps_identified": ["gap 1", "gap 2", ...],
  "carousel_angles": ["angle 1", "angle 2", "angle 3"],
  "analysis_text": "Full markdown analysis following framework template"
}}

Be specific. Use product details from research. Avoid generic observations."""

    user_prompt = f"""# Research to Analyze

{research}

---

# Framework to Apply

{framework}

---

Apply this framework to the research above. Return structured JSON analysis."""

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        temperature=0.3,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract JSON from response
    content = response.content[0].text

    # Try to parse as JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If wrapped in markdown, extract
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
            raise ValueError(f"Could not parse JSON from Claude response: {content[:200]}")


def analyze_research(
    research_path: str,
    pillar_id: str,
    framework_path: str,
    output_path: Optional[str] = None
) -> FrameworkAnalysis:
    """
    Main function: analyze research with framework.

    Args:
        research_path: Path to Obsidian research markdown
        pillar_id: Content pillar ID (e.g., "growth_loops_are_changing")
        framework_path: Path to framework template
        output_path: Optional path to save analysis JSON

    Returns:
        FrameworkAnalysis object (validated)
    """
    # Load API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")

    # Load research and framework
    print(f"\n📄 Loading research from: {research_path}")
    research = load_research(research_path)
    print(f"   ✓ Loaded {len(research)} characters")

    print(f"\n📋 Loading framework from: {framework_path}")
    framework = load_framework(framework_path)
    print(f"   ✓ Loaded framework template")

    # Apply framework
    print(f"\n🤖 Analyzing with Claude...")
    analysis_dict = apply_framework_with_claude(
        research=research,
        framework=framework,
        pillar_name=pillar_id,
        api_key=api_key
    )

    # Add pillar metadata
    analysis_dict["pillar_id"] = pillar_id
    analysis_dict["framework_used"] = framework_path

    # Validate with Pydantic
    print(f"\n✓ Validating analysis structure...")
    analysis = FrameworkAnalysis(**analysis_dict)

    # Save if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(analysis.model_dump(), indent=2),
            encoding="utf-8"
        )
        print(f"\n💾 Saved analysis to: {output_path}")

    return analysis


def display_analysis_summary(analysis: FrameworkAnalysis):
    """Display analysis summary for review."""
    print("\n" + "="*70)
    print("📊 FRAMEWORK ANALYSIS SUMMARY")
    print("="*70)

    print(f"\n🎯 Pillar: {analysis.pillar_id}")
    print(f"📐 Framework: {analysis.framework_used}")

    print(f"\n💡 Key Insights ({len(analysis.key_insights)}):")
    for i, insight in enumerate(analysis.key_insights[:3], 1):
        print(f"   {i}. {insight[:100]}{'...' if len(insight) > 100 else ''}")

    if analysis.growth_loops_identified:
        print(f"\n🔄 Growth Loops Identified ({len(analysis.growth_loops_identified)}):")
        for loop in analysis.growth_loops_identified[:3]:
            print(f"   • {loop}")

    print(f"\n📈 Shifts Mapped ({len(analysis.shifts_mapped)}):")
    for shift, application in list(analysis.shifts_mapped.items())[:3]:
        print(f"   • {shift}: {application[:80]}{'...' if len(application) > 80 else ''}")

    if analysis.gaps_identified:
        print(f"\n🔍 Gaps Identified ({len(analysis.gaps_identified)}):")
        for gap in analysis.gaps_identified[:2]:
            print(f"   • {gap}")

    print(f"\n🎨 Carousel Angles ({len(analysis.carousel_angles)}):")
    for i, angle in enumerate(analysis.carousel_angles, 1):
        print(f"   {i}. {angle}")

    print("\n" + "="*70)
