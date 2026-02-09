"""
Prompt iteration engine.

Automatically adjusts prompts based on eval results to improve match scores.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def analyze_diff_with_claude(
    expected: Dict[str, Any],
    generated: Dict[str, Any],
    differences: List[Dict],
    current_prompt: str
) -> Dict[str, str]:
    """
    Use Claude to analyze what went wrong and suggest prompt improvements.

    Args:
        expected: Expected carousel
        generated: Generated carousel
        differences: List of differences
        current_prompt: Current prompt template

    Returns:
        Dict with suggested prompt adjustments per component
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    analysis_prompt = f"""You are a prompt engineer analyzing why a carousel generation failed to match expectations.

# Expected Output
{format_carousel_for_analysis(expected)}

# Generated Output
{format_carousel_for_analysis(generated)}

# Identified Differences
{format_differences(differences)}

# Current Prompt
{current_prompt}

---

Analyze:
1. What specific parts of the prompt caused the mismatch?
2. What constraints are missing?
3. What instructions need to be tightened?

Return your analysis as JSON:
{{
  "root_cause": "...",
  "prompt_adjustments": {{
    "instructions": "Add/modify: ...",
    "constraints": "Add/modify: ...",
    "examples_guidance": "..."
  }},
  "priority": "high|medium|low"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        temperature=0.3,
        messages=[{"role": "user", "content": analysis_prompt}]
    )

    # Parse Claude's analysis
    import json
    content = response.content[0].text

    # Extract JSON
    if "```json" in content:
        json_start = content.find("```json") + 7
        json_end = content.find("```", json_start)
        content = content[json_start:json_end].strip()

    analysis = json.loads(content)
    return analysis


def format_carousel_for_analysis(carousel: Dict) -> str:
    """Format carousel for Claude analysis."""
    lines = [f"Title: {carousel.get('title', '')}"]
    lines.append(f"Pillar: {carousel.get('pillar', '')}")
    lines.append("\nSlides:")
    for slide in carousel.get("slides", []):
        lines.append(f"  Slide {slide.get('index', slide.get('slide_number', '?'))}:")
        text_lines = slide.get("text_lines", [slide.get("text", "")])
        for line in text_lines:
            lines.append(f"    {line}")
    return "\n".join(lines)


def format_differences(differences: List[Dict]) -> str:
    """Format differences for analysis."""
    if not differences:
        return "No significant differences identified"

    lines = []
    for diff in differences[:5]:  # Top 5 differences
        lines.append(f"Slide {diff.get('slide_index', '?')}:")
        lines.append(f"  Similarity: {diff.get('similarity', 0):.2f}")
        lines.append(f"  Issue: {diff.get('issue', 'unknown')}")
        lines.append(f"  Generated: {diff.get('generated', '')[:100]}...")
        lines.append(f"  Expected: {diff.get('expected', '')[:100]}...")
        lines.append("")
    return "\n".join(lines)


def apply_prompt_adjustments(
    current_prompt: str,
    adjustments: Dict[str, str]
) -> str:
    """
    Apply suggested adjustments to the prompt template.

    Args:
        current_prompt: Current prompt content
        adjustments: Suggested adjustments per component

    Returns:
        Updated prompt
    """
    # For now, append adjustments as additional constraints
    # In future, this could be smarter (replacing sections, etc.)

    additions = []

    if "instructions" in adjustments:
        additions.append(f"\n**Additional Instruction:** {adjustments['instructions']}")

    if "constraints" in adjustments:
        additions.append(f"\n**Additional Constraint:** {adjustments['constraints']}")

    if "examples_guidance" in adjustments:
        additions.append(f"\n**Example Guidance:** {adjustments['examples_guidance']}")

    if additions:
        # Append before </instructions> tag
        if "</instructions>" in current_prompt:
            insert_pos = current_prompt.find("</instructions>")
            updated = (
                current_prompt[:insert_pos] +
                "\n".join(additions) +
                "\n\n" +
                current_prompt[insert_pos:]
            )
            return updated
        else:
            # Append at end
            return current_prompt + "\n\n" + "\n".join(additions)

    return current_prompt


def save_prompt_version(
    prompt_content: str,
    pillar_id: str,
    version: int,
    notes: str = None
) -> str:
    """
    Save a new prompt version to file.

    Args:
        prompt_content: Updated prompt
        pillar_id: Pillar identifier
        version: Version number
        notes: Optional notes

    Returns:
        Path to saved prompt file
    """
    prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "versions"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    filename = f"carousel_generation_{pillar_id}_v{version}.txt"
    file_path = prompts_dir / filename

    # Save prompt
    file_path.write_text(prompt_content, encoding="utf-8")

    # Save metadata
    metadata = {
        "pillar_id": pillar_id,
        "version": version,
        "notes": notes,
        "created_at": str(Path(file_path).stat().st_mtime)
    }

    metadata_path = prompts_dir / f"{filename}.meta.json"
    import json
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return str(file_path)


def iterate_prompt(
    pillar_id: str,
    expected: Dict,
    generated: Dict,
    evaluation: Dict,
    current_prompt: str,
    current_version: int = 1
) -> Dict[str, Any]:
    """
    Main iteration function: analyze failure and improve prompt.

    Args:
        pillar_id: Pillar ID
        expected: Expected carousel
        generated: Generated carousel
        evaluation: Evaluation results
        current_prompt: Current prompt template
        current_version: Current version number

    Returns:
        Dict with new_prompt, analysis, version_number
    """
    print(f"\n🔍 Analyzing failures for {pillar_id}...")

    # Use Claude to analyze
    analysis = analyze_diff_with_claude(
        expected=expected,
        generated=generated,
        differences=evaluation.get("differences", []),
        current_prompt=current_prompt
    )

    print(f"   Root cause: {analysis.get('root_cause', 'Unknown')}")
    print(f"   Priority: {analysis.get('priority', 'medium')}")

    # Apply adjustments
    new_prompt = apply_prompt_adjustments(
        current_prompt,
        analysis.get("prompt_adjustments", {})
    )

    # Save new version
    new_version = current_version + 1
    prompt_path = save_prompt_version(
        prompt_content=new_prompt,
        pillar_id=pillar_id,
        version=new_version,
        notes=analysis.get("root_cause", "")
    )

    print(f"   ✓ New prompt version saved: v{new_version}")
    print(f"   Path: {prompt_path}")

    return {
        "new_prompt": new_prompt,
        "analysis": analysis,
        "version": new_version,
        "prompt_path": prompt_path
    }
