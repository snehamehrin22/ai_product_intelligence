"""
Layer 1: Triage Agent
Classifies raw brain dumps into atomic triage items.
"""
from pathlib import Path
from typing import List
from .schemas import TriageItem
from .llm_clients import call_openrouter, parse_json_response
from datetime import datetime


def load_prompt() -> str:
    """Load the Layer 1 triage system prompt."""
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "layer1_triage_system.txt"
    return prompt_path.read_text(encoding="utf-8")


def triage_braindump(
    raw_text: str,
    date: str = None,
    starting_id: int = 1,
    model: str = "openai/gpt-4o-mini",
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

    # Create user prompt with strict JSON rules
    user_prompt = f"""Date: {date}
Starting ID: T{starting_id:03d}

Input text:
<<<
{raw_text}
>>>

CRITICAL OUTPUT FORMAT:
You MUST return a JSON object with an "items" key containing an array of triage items.

Format:
{{
  "items": [
    {{"Triage ID": "T001", "Raw Text": "...", "Type": "...", "Domain": "...", "Niche Signal": "Yes/No/Weak", "Publishable": "Yes/Possible/No/N/A"}},
    {{"Triage ID": "T002", "Raw Text": "...", "Type": "...", "Domain": "...", "Niche Signal": "Yes/No/Weak", "Publishable": "Yes/Possible/No/N/A"}}
  ]
}}

Rules:
- Return ONLY valid JSON (no markdown, no explanatory text)
- The top-level must be an object with "items" key
- The "items" value must be an array
- Escape all quotes inside strings with \"
- If you run out of tokens, close all open brackets/braces first

Return the JSON object now:"""

    # Call LLM via OpenRouter with guaranteed JSON output
    print(f"🤖 Calling {model} (via OpenRouter) for Layer 1 triage...")
    response = call_openrouter(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=8000,
        response_format={"type": "json_object"}  # Guarantees valid JSON
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

        # Map LLM table column names to schema field names
        field_mapping = {
            "Triage ID": "id",
            "Raw Text": "raw_context",
            "Type": "type",
            "Domain": "domain",
            "Niche Signal": "niche_signal",
            "Publishable": "publishable"
        }

        mapped_items = []
        for idx, item in enumerate(items_data):
            mapped_item = {}
            for llm_key, value in item.items():
                # Map to schema field name
                schema_key = field_mapping.get(llm_key, llm_key.lower().replace(" ", "_"))

                # Convert "Yes"/"No"/"Weak" to boolean for niche_signal
                if schema_key == "niche_signal":
                    mapped_item[schema_key] = value.lower() in ["yes", "true", "weak"]
                # Convert "Yes"/"Possible"/"No" to boolean for publishable
                elif schema_key == "publishable":
                    mapped_item[schema_key] = value.lower() in ["yes", "possible", "true"]
                else:
                    mapped_item[schema_key] = value

            # CRITICAL: Override LLM-generated ID with correct sequential ID
            mapped_item["id"] = f"T{starting_id + idx:03d}"

            # Add date if not present
            if "date" not in mapped_item:
                mapped_item["date"] = date

            # Add personal_or_work if not present (default to "Personal")
            if "personal_or_work" not in mapped_item:
                mapped_item["personal_or_work"] = "Personal"

            # Add tags if not present (extract from domain as fallback)
            if "tags" not in mapped_item or not mapped_item["tags"]:
                # Use domain as tags if tags are missing
                if "domain" in mapped_item:
                    mapped_item["tags"] = mapped_item["domain"].lower().replace(", ", ",")
                else:
                    mapped_item["tags"] = "uncategorized"

            # Convert tags to comma-separated string if it's a list
            if "tags" in mapped_item and isinstance(mapped_item["tags"], list):
                mapped_item["tags"] = ", ".join(mapped_item["tags"])

            mapped_items.append(mapped_item)

        # Validate with Pydantic
        items = [TriageItem(**item) for item in mapped_items]

        print(f"✓ Parsed {len(items)} triage items\n")
        return items

    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}")
        print(f"Raw response preview: {response[:500]}...")
        raise ValueError(f"Failed to parse triage response: {e}")
