"""
LLM-based classification of cognitive blocks.
"""
import json
import os
from pathlib import Path
from openai import OpenAI
from pydantic import ValidationError

from ..schemas import CognitiveBlock, BlockClassification


def load_prompt(prompt_name: str) -> str:
    """Load a prompt from the prompts/ folder."""
    prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def classify_block(block: CognitiveBlock, api_key: str = None) -> BlockClassification:
    """
    Classify a cognitive block using OpenAI.

    Args:
        block: The cognitive block to classify
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)

    Returns:
        Validated BlockClassification object

    Raises:
        ValueError: If API key is missing or response is invalid
        ValidationError: If LLM response doesn't match schema
    """
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    # Load system prompt from file
    system_prompt = load_prompt("block_classifier_system")

    client = OpenAI(api_key=api_key)

    # Format user message using the template in the prompt
    user_message = system_prompt.replace("{BLOCK_ID}", block.block_id).replace("{BLOCK_TEXT}", block.block_text)

    # Make API call with guaranteed JSON response
    resp = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_tokens=800
    )

    # Parse JSON response
    text_out = resp.choices[0].message.content
    data = json.loads(text_out)

    # Validate with Pydantic (throws ValidationError if invalid)
    validated_classification = BlockClassification(**data)

    return validated_classification
