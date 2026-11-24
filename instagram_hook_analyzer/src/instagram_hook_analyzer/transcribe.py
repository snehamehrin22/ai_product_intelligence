"""Transcribe reel audio and split the transcript into hook and body."""

import tempfile
from typing import Dict

import requests
from openai import OpenAI

HOOK_SECONDS = 5.0


def split_hook_body(audio_url: str, hook_seconds: float = HOOK_SECONDS) -> Dict[str, str]:
    """Transcribe audio and split it at a time boundary.

    Args:
        audio_url: Direct URL of the reel's audio.
        hook_seconds: Segments starting before this many seconds form the hook.

    Returns:
        Dict with hook, body and transcript. Empty strings if there is no audio
        or transcription fails; the error is returned under "error".
    """
    empty = {"hook": "", "body": "", "transcript": "", "error": ""}
    if not audio_url:
        return {**empty, "error": "no audio_url"}
    try:
        resp = requests.get(audio_url, timeout=60)
        resp.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            f.write(resp.content)
            f.flush()
            t = OpenAI().audio.transcriptions.create(
                model="whisper-1",
                file=open(f.name, "rb"),
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
    except Exception as e:  # keep one bad reel from killing the batch
        return {**empty, "error": str(e)[:200]}

    hook = " ".join(s.text.strip() for s in t.segments if s.start < hook_seconds)
    body = " ".join(s.text.strip() for s in t.segments if s.start >= hook_seconds)
    return {"hook": hook, "body": body, "transcript": t.text.strip(), "error": ""}
