"""Analyze a reel's edit, typography and imagery into a reusable style spec.

Usage:
    infisical run -- python scripts/analyze_video.py "/path/to/video.mp4"
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openai import OpenAI  # noqa: E402

from instagram_video_analyzer import media, vision  # noqa: E402
from instagram_video_analyzer.schemas import AudioInfo, Shot, VideoStyleSpec  # noqa: E402


def make_proxy(video: Path, out: Path) -> Path:
    """360p/30fps proxy so cut detection doesn't re-decode 4K HEVC (took ~8 min on the source)."""
    if not out.exists():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-an", "-vf", "fps=30,scale=360:-2",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", str(out)], check=True)
    return out


def main() -> None:
    """Run the full pipeline; every stage caches to data/<video>/ so reruns resume."""
    video = Path(sys.argv[1]).expanduser()
    work = ROOT / "data" / video.stem.replace(" ", "_").lower()
    work.mkdir(parents=True, exist_ok=True)
    client = OpenAI()

    info = media.probe(video)
    proxy = make_proxy(video, work / "proxy.mp4")
    ranges = media.build_shots(media.detect_cuts(proxy), info["duration"])
    print(f"{info['width']}x{info['height']} @{info['fps']:.0f}fps, {info['duration']:.1f}s, {len(ranges)} shots")

    shots, times_by_shot = [], {}
    for i, (s, e) in enumerate(ranges):
        n = min(5, 3 + int((e - s) // 4))
        times = [s + 0.1 + (e - s - 0.2) * k / (n - 1) for k in range(n)] if e - s > 0.5 else [(s + e) / 2]
        frames = [str(media.extract_frame(video, t, work / "frames" / f"s{i:02d}_{k}.jpg")) for k, t in enumerate(times)]
        mid = Path(frames[len(frames) // 2])
        shots.append(Shot(index=i, start=round(s, 2), end=round(e, 2), duration=round(e - s, 2),
                          palette=media.palette(mid), ocr_text=media.ocr(mid), frames=frames))
        times_by_shot[i] = times

    for shot in shots:
        cache = work / f"shot_{shot.index:02d}.json"
        if cache.exists():
            shot.analysis = vision.ShotAnalysis(**json.loads(cache.read_text()))
        else:
            shot.analysis = vision.analyze_shot(client, shot, times_by_shot[shot.index])
            cache.write_text(shot.analysis.model_dump_json(indent=2))
        print(f"  shot {shot.index:02d} {shot.start:6.2f}-{shot.end:6.2f}  {shot.analysis.shot_type}: "
              f"{len(shot.analysis.text_overlays)} text overlay(s)")

    audio_path = media.extract_audio(video, work / "audio.mp3")
    audio = vision.transcribe(client, audio_path)
    audio = AudioInfo(**{**audio.model_dump(), **media.audio_levels(video)})

    overall = media.palette(Path(shots[len(shots) // 2].frames[0]), k=6)
    spec = VideoStyleSpec(source=video.name, duration_s=round(info["duration"], 2),
                          resolution=f"{info['width']}x{info['height']}", fps=info["fps"],
                          pacing=media.pacing(ranges, info["duration"]), palette=overall, shots=shots, audio=audio)
    spec.style_summary = vision.summarize(client, json.loads(spec.model_dump_json(exclude={"audio": {"words"}})))

    (work / "style_spec.json").write_text(spec.model_dump_json(indent=2))
    (work / "style_recipe.md").write_text(f"# Style recipe: {video.name}\n\n{spec.style_summary}\n")
    print(f"\nWrote {work/'style_spec.json'}\nWrote {work/'style_recipe.md'}")


if __name__ == "__main__":
    main()
