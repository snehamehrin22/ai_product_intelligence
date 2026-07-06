"""Utility functions for the research agent."""
from pathlib import Path


def load_prompt(prompt_name: str) -> str:
    """Load prompt from prompts/ folder."""
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.txt"
    return prompt_path.read_text(encoding="utf-8")
