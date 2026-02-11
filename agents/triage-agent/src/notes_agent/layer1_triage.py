"""
Layer 1: Triage Agent
Classifies raw brain dumps into atomic triage items.
"""
from pathlib import Path
from typing import List
from .schemas import TriageItem
from .llm_clients import call_deepseek, parse_json_response
from datetime import datetime


def load_prompt() -> str:
    """Load the Layer 1 triage system prompt."""
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "layer1_triage_system.txt"
    return prompt_path.read_text(encoding="utf-8")


def triage_braindump(
    raw_text: str,
    date: str = None,
    starting_id: int = 1,
    model: str = "deepseek-chat",
    temperature: float = 0.2
) -> List[TriageItem]:
    """
    Triage a raw brain dump into classified atomic items.

    Args:
        raw_text: Raw stream-of-consciousness text
        date: Date in YYYY-MM-DD format (defaults to today)
        starting_id: Starting ID number for items (e.g., 1 for T001)
        model: Model to use (default: deepseek-chat)
        temperature: Sampling temperature

    Returns:
        List of TriageItem objects

    Raises:
        ValueError: If LLM response is invalid
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Load system prompt
    system_prompt = load_prompt()

    # Create user prompt
    user_prompt = f"""Date: {date}
Starting ID: T{starting_id:03d}

Input text:
<<<
{raw_text}
>>>

Return ONLY the JSON array. No commentary."""

    # Call LLM
    print(f"🤖 Calling {model} for Layer 1 triage...")
    response = call_deepseek(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=4000
    )

    # Parse response
    try:
        data = parse_json_response(response)

        # Handle both array and object with "items" key
        if isinstance(data, list):
            items_data = data
        elif isinstance(data, dict) and "items" in data:
            items_data = data["items"]
        else:
            raise ValueError(f"Unexpected response format: {type(data)}")

        # Validate with Pydantic
        items = [TriageItem(**item) for item in items_data]

        print(f"✓ Parsed {len(items)} triage items\n")
        return items

    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}")
        print(f"Raw response preview: {response[:500]}...")
        raise ValueError(f"Failed to parse triage response: {e}")
