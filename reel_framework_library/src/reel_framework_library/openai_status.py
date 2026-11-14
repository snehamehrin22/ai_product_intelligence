"""OpenAI connection check: is the key valid and is the transcription model available?"""

import requests

from .config import TRANSCRIPTION_MODEL


def check_openai(token: str) -> str:
    """Confirm the key works by reading model metadata (free, no tokens used).

    Returns:
        A short status line.

    Raises:
        RuntimeError: If OpenAI rejects the key or the model.
    """
    response = requests.get(
        f"https://api.openai.com/v1/models/{TRANSCRIPTION_MODEL}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if response.status_code != 200:
        # Status only; the body can echo parts of the key.
        raise RuntimeError(f"OpenAI returned HTTP {response.status_code} for model {TRANSCRIPTION_MODEL}")
    return f"model {TRANSCRIPTION_MODEL} available"
