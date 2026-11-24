"""LLM layer: per-shot vision analysis, Whisper transcript, and the final style recipe."""
import base64
import json
from pathlib import Path
from typing import List

from openai import OpenAI

from .schemas import AudioInfo, Shot, ShotAnalysis

PROMPTS = Path(__file__).resolve().parents[2] / "prompts"
MODEL = "gpt-4o"


def load_prompt(name: str) -> str:
    """Load a prompt from prompts/."""
    return (PROMPTS / f"{name}.txt").read_text(encoding="utf-8")


def _b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def analyze_shot(client: OpenAI, shot: Shot, times: List[float]) -> ShotAnalysis:
    """Send a shot's frames to the vision model and validate the JSON with Pydantic."""
    system = load_prompt("shot_system").replace("{schema}", json.dumps(ShotAnalysis.model_json_schema()))
    content = [{"type": "text", "text": f"Shot {shot.index}: {shot.start:.2f}s-{shot.end:.2f}s. OCR cross-check: {shot.ocr_text!r}"}]
    for path, t in zip(shot.frames, times):
        content.append({"type": "text", "text": f"Frame at {t:.2f}s"})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{_b64(path)}", "detail": "high"}})
    resp = client.chat.completions.create(
        model=MODEL, response_format={"type": "json_object"}, temperature=0.2, max_tokens=3000,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": content}])
    return ShotAnalysis(**json.loads(resp.choices[0].message.content))


def transcribe(client: OpenAI, audio_path: Path) -> AudioInfo:
    """Whisper transcript with word timestamps (needed to see how text/cuts line up with speech)."""
    with audio_path.open("rb") as f:
        r = client.audio.transcriptions.create(model="whisper-1", file=f, response_format="verbose_json",
                                               timestamp_granularities=["word"])
    return AudioInfo(transcript=r.text, words=[{"w": w.word, "s": w.start, "e": w.end} for w in (r.words or [])])


def summarize(client: OpenAI, breakdown: dict) -> str:
    """One call over the whole breakdown to produce the reusable style recipe."""
    resp = client.chat.completions.create(
        model=MODEL, response_format={"type": "json_object"}, temperature=0.2, max_tokens=4000,
        messages=[{"role": "system", "content": load_prompt("summary_system")},
                  {"role": "user", "content": json.dumps(breakdown)}])
    return json.loads(resp.choices[0].message.content)["style_summary"]
