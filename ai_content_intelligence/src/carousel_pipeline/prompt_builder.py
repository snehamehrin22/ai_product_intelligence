"""
Modular prompt builder for carousel generation.

Assembles prompt components dynamically based on pillar and training examples.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_metadata() -> Dict[str, Any]:
    """Load carousel training metadata."""
    metadata_path = Path(__file__).parent.parent.parent / "config/carousel_training_metadata.json"
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_prompt_template() -> str:
    """Load the carousel generation system prompt template."""
    template_path = Path(__file__).parent.parent.parent / "prompts/carousel_generation_system.txt"
    return template_path.read_text(encoding="utf-8")


def load_framework(pillar_id: str) -> str:
    """
    Load framework file for a specific pillar.

    Args:
        pillar_id: Pillar identifier (e.g., "pillar_01")

    Returns:
        Framework content as string
    """
    metadata = load_metadata()
    framework_file = metadata["pillar_metadata"][pillar_id]["framework_file"]
    framework_path = Path(__file__).parent.parent.parent / framework_file

    if not framework_path.exists():
        raise FileNotFoundError(f"Framework not found: {framework_path}")

    return framework_path.read_text(encoding="utf-8")


def load_training_examples(pillar_id: str) -> List[str]:
    """
    Load ALL training examples for a pillar (general + pillar-specific).

    Args:
        pillar_id: Pillar identifier (e.g., "pillar_01")

    Returns:
        List of carousel example texts
    """
    metadata = load_metadata()
    training_base = Path(__file__).parent.parent.parent / "data/training_carousels"

    examples = []

    # Load general voice examples
    general_folder = training_base / "general_voice"
    for filename in metadata["general_voice"]:
        example_path = general_folder / filename
        if example_path.exists():
            examples.append(example_path.read_text(encoding="utf-8"))

    # Load pillar-specific examples
    pillar_metadata = metadata["pillar_metadata"][pillar_id]
    voice_folder = training_base / pillar_metadata["voice_folder"]

    # Get pillar example files from metadata
    pillar_key = f"{pillar_id}_{pillar_metadata['id'].replace('_', '_')}"
    # Map pillar_01 -> pillar_01_growth_loops
    if pillar_id == "pillar_01":
        pillar_key = "pillar_01_growth_loops"
    elif pillar_id == "pillar_02":
        pillar_key = "pillar_02_measurement_gap"
    elif pillar_id == "pillar_03":
        pillar_key = "pillar_03_thinking_layer"

    for filename in metadata[pillar_key]:
        example_path = voice_folder / filename
        if example_path.exists():
            examples.append(example_path.read_text(encoding="utf-8"))

    return examples


def build_carousel_prompt(
    research: str,
    pillar_id: str,
    optional_constraints: str = "",
    custom_template_path: str = None
) -> str:
    """
    Build complete carousel generation prompt.

    Args:
        research: App analysis/research content
        pillar_id: Pillar identifier (e.g., "pillar_01")
        optional_constraints: Optional constraints string
        custom_template_path: Optional path to custom prompt template (for iterations)

    Returns:
        Complete prompt ready for LLM
    """
    metadata = load_metadata()
    pillar_meta = metadata["pillar_metadata"][pillar_id]

    # Load components
    if custom_template_path:
        template = Path(custom_template_path).read_text(encoding="utf-8")
    else:
        template = load_prompt_template()
    framework = load_framework(pillar_id)
    examples = load_training_examples(pillar_id)

    # Format examples with separators
    examples_text = "\n\n---\n\n".join(examples)

    # Get carousel goal
    carousel_goal = pillar_meta["carousel_goal"]

    # Fill template
    prompt = template.format(
        app_analysis=research,
        framework=framework,
        examples=examples_text,
        carousel_goal=carousel_goal,
        optional_constraints=optional_constraints if optional_constraints else "None"
    )

    return prompt


def get_pillar_metadata(pillar_id: str) -> Dict[str, Any]:
    """
    Get metadata for a specific pillar.

    Args:
        pillar_id: Pillar identifier

    Returns:
        Pillar metadata dict
    """
    metadata = load_metadata()
    return metadata["pillar_metadata"][pillar_id]
