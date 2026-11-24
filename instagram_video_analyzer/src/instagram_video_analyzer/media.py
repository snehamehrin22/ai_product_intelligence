"""Deterministic media work: probing, cut detection, frame extraction, palette, OCR, audio stats."""
import json
import re
import statistics
import subprocess
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from .schemas import Pacing

FRAME_WIDTH = 720  # 4K frames are wasted on the vision model; 720 keeps type legible


def probe(video: Path) -> dict:
    """Return duration, resolution and fps via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    num, den = data["streams"][0]["r_frame_rate"].split("/")
    return {"duration": float(data["format"]["duration"]),
            "width": data["streams"][0]["width"], "height": data["streams"][0]["height"],
            "fps": float(num) / float(den)}


def detect_cuts(video: Path, threshold: float = 0.25) -> List[float]:
    """Find cut timestamps with ffmpeg's scene score (runs on a downscaled stream for speed)."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(video), "-vf",
         f"scale=360:-2,select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
        capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", proc.stderr)]


def build_shots(cuts: List[float], duration: float, min_len: float = 0.25) -> List[Tuple[float, float]]:
    """Turn cut times into (start, end) pairs, merging slivers shorter than min_len (flash frames)."""
    bounds = [0.0] + [c for c in cuts if c - 0.0 > 0] + [duration]
    shots: List[Tuple[float, float]] = []
    for start, end in zip(bounds, bounds[1:]):
        if shots and end - start < min_len:
            shots[-1] = (shots[-1][0], end)
        else:
            shots.append((start, end))
    return shots


def extract_frame(video: Path, t: float, out: Path) -> Path:
    """Grab one downscaled frame at time t."""
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
         "-vf", f"scale={FRAME_WIDTH}:-2", "-q:v", "3", str(out)], check=True)
    return out


def palette(image_path: Path, k: int = 4) -> List[str]:
    """Dominant colors of a frame as hex, most common first."""
    img = Image.open(image_path).convert("RGB").resize((96, 170))
    px = np.asarray(img).reshape(-1, 3)
    km = KMeans(n_clusters=k, n_init=3, random_state=0).fit(px)
    order = np.argsort(-np.bincount(km.labels_))
    return ["#%02x%02x%02x" % tuple(int(c) for c in km.cluster_centers_[i]) for i in order]


def ocr(image_path: Path) -> str:
    """Cheap OCR pass; the vision model is the source of truth, this is a cross-check."""
    import pytesseract
    return " ".join(pytesseract.image_to_string(Image.open(image_path)).split())


def pacing(shots: List[Tuple[float, float]], duration: float) -> Pacing:
    """Summary stats on shot length."""
    lens = [e - s for s, e in shots]
    return Pacing(shot_count=len(lens), avg_shot_s=round(statistics.mean(lens), 2),
                  median_shot_s=round(statistics.median(lens), 2), shortest_s=round(min(lens), 2),
                  longest_s=round(max(lens), 2), cuts_per_minute=round((len(lens) - 1) / duration * 60, 1))


def extract_audio(video: Path, out: Path) -> Path:
    """16 kHz mono mp3 for Whisper (keeps the upload under the 25 MB limit)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "48k", str(out)], check=True)
    return out


def audio_levels(video: Path) -> dict:
    """Mean/max volume and silent gaps via ffmpeg filters."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(video), "-vn", "-af", "volumedetect,silencedetect=noise=-35dB:d=0.4",
         "-f", "null", "-"], capture_output=True, text=True)
    err = proc.stderr
    mean = re.search(r"mean_volume: (-?[\d.]+)", err)
    mx = re.search(r"max_volume: (-?[\d.]+)", err)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return {"mean_volume_db": float(mean.group(1)) if mean else None,
            "max_volume_db": float(mx.group(1)) if mx else None,
            "silent_segments": [[s, e] for s, e in zip(starts, ends)]}
