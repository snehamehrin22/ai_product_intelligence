"""
Cognitive block splitter - uses LLM to split raw journal text into cognitive blocks.
"""
import json
import os
from typing import List
from pathlib import Path
from openai import OpenAI
from pydantic import ValidationError

from .schemas import CognitiveBlock, BlockSplitResponse


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from the prompts/ folder.

    Args:
        prompt_name: Name of the prompt file (without .txt extension)

    Returns:
        Prompt text as string
    """
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def split_into_blocks(raw_text: str, api_key: str = None) -> List[CognitiveBlock]:
    """
    Split raw journal text into cognitive blocks using OpenAI.

    Args:
        raw_text: Raw journal entry text
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)

    Returns:
        List of validated CognitiveBlock objects

    Raises:
        ValueError: If API key is missing or response is invalid
        ValidationError: If LLM response doesn't match schema
    """
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    # Load system prompt from file
    system_prompt = load_prompt("block_splitter_system")

    client = OpenAI(api_key=api_key)

    # Make API call with guaranteed JSON response
    resp = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please split this journal entry:\n\n{raw_text}"}
        ],
        temperature=0.2,
        max_tokens=4000
    )

    # Parse JSON response
    text_out = resp.choices[0].message.content
    data = json.loads(text_out)

    # Validate with Pydantic (throws ValidationError if invalid)
    validated_response = BlockSplitResponse(**data)

    return validated_response.blocks
