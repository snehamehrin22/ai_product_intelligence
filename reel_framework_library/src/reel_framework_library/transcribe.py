"""Transcribe reel audio with Whisper and save one JSON file per reel.

The OpenAI client and the audio downloader are passed in, so tests never touch
the network or spend money.
"""

import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from pydantic import ValidationError

from .fetch import append_errors
from .schemas import Transcript


def transcript_path(transcripts_dir: Path, handle: str, shortcode: str) -> Path:
    """Where one reel's transcript is saved."""
    return transcripts_dir / handle / f"{shortcode}.json"


def load_audio_urls(raw_dir: Path) -> Dict[Tuple[str, str], str]:
    """Map (handle, shortcode) to the reel's audio URL, from the raw scraper files.

    The scored CSV doesn't carry audio URLs on purpose (they expire); the raw
    files are the source of truth.
    """
    urls: Dict[Tuple[str, str], str] = {}
    for path in sorted(raw_dir.glob("*.json")):
        for item in json.loads(path.read_text(encoding="utf-8")):
            if item.get("audioUrl") and item.get("shortCode"):
                urls[(path.stem, item["shortCode"])] = item["audioUrl"]
    return urls


def queue_from_scored(scored_csv: Path) -> List[Dict[str, Any]]:
    """Reels to transcribe, best first: highest outlier ratio, then the too-new ones.

    Order matters only if a run is interrupted: the most useful reels are done first.
    """
    with open(scored_csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows.sort(key=lambda r: (r["outlier_ratio"] == "", -float(r["outlier_ratio"] or 0)))
    return rows


def pending(queue: List[Dict[str, Any]], transcripts_dir: Path) -> List[Dict[str, Any]]:
    """Reels without a saved transcript, so re-runs resume instead of repaying."""
    return [r for r in queue if not transcript_path(transcripts_dir, r["handle"], r["shortcode"]).exists()]


def estimate_cost(queue: List[Dict[str, Any]], usd_per_minute: float) -> Tuple[float, float]:
    """Return (total audio minutes, estimated USD) for a queue of reels."""
    minutes = sum(float(r.get("duration_seconds") or 0) for r in queue) / 60
    return round(minutes, 1), round(minutes * usd_per_minute, 2)


def download_audio(url: str) -> bytes:
    """Fetch an audio file. Instagram CDN links expire, so this can fail with 403/410."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content


def to_transcript(handle: str, shortcode: str, model: str, response: Any) -> Transcript:
    """Validate a Whisper verbose_json response into a Transcript.

    Never trust the raw response: it is parsed through Pydantic so a malformed
    reply becomes an error record, not a half-empty file.

    Raises:
        pydantic.ValidationError: If the response is missing required fields.
    """
    data = response.model_dump() if hasattr(response, "model_dump") else dict(response)
    return Transcript(
        handle=handle,
        shortcode=shortcode,
        model=model,
        language=data.get("language"),
        audio_duration_seconds=data.get("duration"),
        text=(data.get("text") or "").strip(),
        segments=[
            {
                "start": s["start"],
                "end": s["end"],
                "text": s["text"].strip(),
                "no_speech_prob": s.get("no_speech_prob"),
                "avg_logprob": s.get("avg_logprob"),
            }
            for s in (data.get("segments") or [])
        ],
    )


def transcribe_one(
    client: Any,
    model: str,
    row: Dict[str, Any],
    audio_url: str,
    transcripts_dir: Path,
    downloader: Callable[[str], bytes] = download_audio,
) -> Transcript:
    """Download one reel's audio, transcribe it, save the validated result.

    Raises:
        Exception: Any download, API or validation failure; the caller records it.
    """
    audio = downloader(audio_url)
    response = client.audio.transcriptions.create(
        model=model,
        file=(f"{row['shortcode']}.mp4", audio),
        response_format="verbose_json",
    )
    transcript = to_transcript(row["handle"], row["shortcode"], model, response)
    path = transcript_path(transcripts_dir, row["handle"], row["shortcode"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(transcript.model_dump_json(indent=1), encoding="utf-8")
    return transcript


def transcribe_all(
    client: Any,
    model: str,
    queue: List[Dict[str, Any]],
    audio_urls: Dict[Tuple[str, str], str],
    transcripts_dir: Path,
    errors_path: Path,
    workers: int = 4,
    downloader: Callable[[str], bytes] = download_audio,
    progress_every: int = 25,
) -> Dict[str, Any]:
    """Transcribe a queue of reels with a small thread pool.

    Failures are written to errors.jsonl and never stop the run.

    Returns:
        Summary: done, failed (list of shortcodes), skipped_no_audio.
    """
    done, failed, no_audio = 0, [], 0
    jobs = []
    for row in queue:
        url = audio_urls.get((row["handle"], row["shortcode"]))
        if url is None:
            no_audio += 1
            append_errors(errors_path, [{"handle": row["handle"], "shortcode": row["shortcode"], "stage": "transcribe", "error": "no audio url"}])
        else:
            jobs.append((row, url))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(transcribe_one, client, model, row, url, transcripts_dir, downloader): row
            for row, url in jobs
        }
        for count, future in enumerate(as_completed(futures), start=1):
            row = futures[future]
            try:
                future.result()
                done += 1
            except (ValidationError, Exception) as exc:  # noqa: BLE001 - record and continue
                failed.append(row["shortcode"])
                append_errors(errors_path, [{"handle": row["handle"], "shortcode": row["shortcode"], "stage": "transcribe", "error": f"{type(exc).__name__}: {str(exc)[:200]}"}])
            if count % progress_every == 0 or count == len(futures):
                print(f"  {count}/{len(futures)} processed ({done} ok, {len(failed)} failed)", flush=True)

    return {"done": done, "failed": failed, "skipped_no_audio": no_audio}
