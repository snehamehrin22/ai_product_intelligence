"""Beat extraction and framework clustering. Logic only; see scripts/pilot_frameworks.py."""

import csv
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional

from openai import OpenAI

from .config import (
    EXTRACTION_MODEL,
    MIN_SPEECH_COVERAGE,
    MIN_WORDS,
    MIN_WORDS_PER_MINUTE,
    PROMPTS_DIR,
    SCORED_CSV,
    TRANSCRIPTS_DIR,
)
from .schemas import FrameworkDraft, FrameworkSet, ReelBeats, Transcript


def load_prompt(name: str) -> str:
    """Read a prompt from prompts/ so it can be edited without touching code."""
    return (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")


def speech_coverage(t: Transcript) -> float:
    """Share of the video covered by transcript segments (not no_speech_prob, which drops music-backed speech)."""
    if not t.audio_duration_seconds:
        return 0.0
    return min(1.0, sum(s.end - s.start for s in t.segments) / t.audio_duration_seconds)


def has_speech(t: Transcript) -> bool:
    """Apply the PRD speech thresholds to one transcript."""
    words = len(t.text.split())
    dur = t.audio_duration_seconds or 0
    wpm = words / (dur / 60) if dur else 0
    return speech_coverage(t) >= MIN_SPEECH_COVERAGE and words >= MIN_WORDS and wpm >= MIN_WORDS_PER_MINUTE


def load_transcripts() -> Dict[str, Transcript]:
    """Load every saved transcript keyed 'handle/shortcode'."""
    out = {}
    for f in sorted(TRANSCRIPTS_DIR.glob("*/*.json")):
        t = Transcript(**json.loads(f.read_text(encoding="utf-8")))
        out[f"{t.handle}/{t.shortcode}"] = t
    return out


def outlier_ratios() -> Dict[str, float]:
    """Outlier ratio per 'handle/shortcode' from the scored CSV (blank = unscored)."""
    with open(SCORED_CSV, encoding="utf-8") as fh:
        return {
            f"{r['handle']}/{r['shortcode']}": float(r["outlier_ratio"])
            for r in csv.DictReader(fh)
            if r["outlier_ratio"]
        }


def pick_pilot(transcripts: Dict[str, Transcript], ratios: Dict[str, float], n_creators: int, per_creator: int) -> List[str]:
    """Choose pilot reels: creators with 12+ speech reels, spread evenly by name; each creator's best by outlier ratio.

    Ranking is within creator, so one viral account can't dominate the sample.
    """
    by_creator: Dict[str, List[str]] = {}
    for rid, t in transcripts.items():
        if rid in ratios and has_speech(t):
            by_creator.setdefault(t.handle, []).append(rid)
    eligible = sorted(h for h, ids in by_creator.items() if len(ids) >= 12)
    step = max(1, len(eligible) // n_creators)
    chosen = eligible[::step][:n_creators]
    picked: List[str] = []
    for h in chosen:
        picked += sorted(by_creator[h], key=lambda r: -ratios[r])[:per_creator]
    return picked


def _chat_json(client: OpenAI, system: str, user: str) -> dict:
    """One JSON-mode completion; the caller validates with Pydantic."""
    resp = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=4000,
    )
    return json.loads(resp.choices[0].message.content)


def check_beat_coverage(beats: ReelBeats, n_segments: int) -> None:
    """Raise if beats leave gaps, overlap, or miss the ends: the LLM can't be trusted to tile segments."""
    expected = 0
    for b in beats.beats:
        if b.first_segment != expected or b.last_segment < b.first_segment:
            raise ValueError(f"beats not contiguous at segment {expected}")
        expected = b.last_segment + 1
    if expected != n_segments:
        raise ValueError(f"beats cover {expected} of {n_segments} segments")


def extract_beats(client: OpenAI, t: Transcript, retries: int = 2) -> ReelBeats:
    """Label a reel's beats; on a validation failure retry with the error fed back, then raise."""
    numbered = "\n".join(f"{i}: {s.text.strip()}" for i, s in enumerate(t.segments))
    last: Optional[Exception] = None
    prompt = numbered
    for _ in range(retries + 1):
        if last:
            prompt = f"{numbered}\n\nYour previous answer was rejected: {str(last)[:300]}\nFix it. Cover every segment 0-{len(t.segments) - 1} exactly once and use only the allowed labels."
        try:
            beats = ReelBeats(**_chat_json(client, load_prompt("beat_extractor_system"), prompt))
            check_beat_coverage(beats, len(t.segments))
            return beats
        except ValueError as exc:  # pydantic.ValidationError subclasses ValueError
            last = exc
    raise ValueError(f"beat extraction failed: {last}")


def beat_shares(t: Transcript, beats: ReelBeats) -> List[dict]:
    """Per beat: function, purpose, start/end seconds and share of the reel's words (all computed, not LLM-claimed)."""
    total = max(1, len(t.text.split()))
    out = []
    for b in beats.beats:
        segs = t.segments[b.first_segment : b.last_segment + 1]
        words = sum(len(s.text.split()) for s in segs)
        out.append({
            "function": b.function,
            "purpose": b.purpose,
            "start": round(segs[0].start, 1),
            "end": round(segs[-1].end, 1),
            "word_share": round(words / total, 2),
            "text": " ".join(s.text.strip() for s in segs),
        })
    return out


def _validate_assignment(fs: FrameworkSet, ids: set) -> None:
    """Raise unless every reel is in exactly one framework and each framework is well-formed."""
    seen: Dict[str, int] = {}
    for f in fs.frameworks:
        if f.name != "Unclustered" and (len(f.beat_pattern) < 2 or len(f.beat_pattern) != len(f.beat_notes)):
            raise ValueError(f"{f.name}: need 2+ beats and one note per beat")
        for rid in f.reel_ids:
            seen[rid] = seen.get(rid, 0) + 1
    unknown = set(seen) - ids
    dup = [r for r, c in seen.items() if c > 1]
    missing = ids - set(seen)
    if unknown or dup or missing:
        raise ValueError(f"bad assignment: unknown={sorted(unknown)} duplicated={dup} missing={sorted(missing)}")


def cluster_frameworks(client: OpenAI, summaries: List[dict], retries: int = 2) -> FrameworkSet:
    """Propose frameworks from beat summaries; retry with the error fed back until every reel is placed once."""
    ids = {s["id"] for s in summaries}
    base = json.dumps(summaries)
    prompt, last = base, None
    for _ in range(retries + 1):
        if last:
            prompt = f"{base}\n\nYour previous answer was rejected: {last}\nReturn the full corrected set."
        try:
            fs = FrameworkSet(**_chat_json(client, load_prompt("framework_cluster_system"), prompt))
            _validate_assignment(fs, ids)
            return fs
        except ValueError as exc:
            last = str(exc)[:500]
    # The model won't place every reel. Rather than lose the run, park the leftovers visibly.
    fs = FrameworkSet(**_chat_json(client, load_prompt("framework_cluster_system"), base))
    placed = {r for f in fs.frameworks for r in f.reel_ids}
    for f in fs.frameworks:
        f.reel_ids = [r for r in f.reel_ids if r in ids]
    leftovers = sorted(ids - placed)
    if leftovers:
        un = next((f for f in fs.frameworks if f.name == "Unclustered"), None)
        if un:
            un.reel_ids += leftovers
        else:
            fs.frameworks.append(FrameworkDraft(name="Unclustered", beat_pattern=[], beat_notes=[], suits_content="not placed by the model", reel_ids=leftovers))
        print(f"WARNING: {len(leftovers)} reels not placed by the model, put in Unclustered")
    return fs


def framework_stats(fs: FrameworkSet, transcripts: Dict[str, Transcript], ratios: Dict[str, float]) -> Dict[str, dict]:
    """Deterministic stats per framework: size, creators, median length/words/outlier ratio."""
    stats = {}
    for f in fs.frameworks:
        ts = [transcripts[r] for r in f.reel_ids]
        stats[f.name] = {
            "reels": len(ts),
            "creators": len({t.handle for t in ts}),
            "median_seconds": round(statistics.median(t.audio_duration_seconds or 0 for t in ts)),
            "median_words": round(statistics.median(len(t.text.split()) for t in ts)),
            "median_outlier": round(statistics.median(ratios[r] for r in f.reel_ids), 2),
        }
    return stats
