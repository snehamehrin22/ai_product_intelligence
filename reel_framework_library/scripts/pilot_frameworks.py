"""Pilot: extract beats from ~40 reels, cluster into frameworks, write review cards.

Examples:
    python scripts/pilot_frameworks.py
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.config import (  # noqa: E402
    BEATS_DIR,
    ERRORS_JSONL,
    FRAMEWORKS_DIR,
    PILOT_CREATORS,
    PILOT_REELS_PER_CREATOR,
    PROJECT_ROOT,
)
from reel_framework_library.frameworks import (  # noqa: E402
    beat_shares,
    cluster_frameworks,
    extract_beats,
    framework_stats,
    load_transcripts,
    outlier_ratios,
    pick_pilot,
)


def main() -> int:
    """Run the pilot; return a process exit code."""
    load_dotenv(PROJECT_ROOT / ".env")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    transcripts = load_transcripts()
    ratios = outlier_ratios()
    picked = pick_pilot(transcripts, ratios, PILOT_CREATORS, PILOT_REELS_PER_CREATOR)
    print(f"pilot: {len(picked)} reels, {len({r.split('/')[0] for r in picked})} creators")

    BEATS_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORKS_DIR.mkdir(parents=True, exist_ok=True)

    def one(rid: str):
        path = BEATS_DIR / f"{rid.replace('/', '__')}.json"
        t = transcripts[rid]
        if path.exists():
            return rid, json.loads(path.read_text(encoding="utf-8")), None
        try:
            beats = extract_beats(client, t)
        except ValueError as exc:
            return rid, None, str(exc)
        rec = {"id": rid, "hook_type": beats.hook_type, "thesis": beats.thesis, "beats": beat_shares(t, beats)}
        path.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        return rid, rec, None

    with ThreadPoolExecutor(4) as ex:
        results = list(ex.map(one, picked))
    ok = {rid: rec for rid, rec, err in results if rec}
    # Failures are logged, never mixed into the corpus (project lesson from the first analyzer).
    with open(ERRORS_JSONL, "a", encoding="utf-8") as fh:
        for rid, _, err in results:
            if err:
                fh.write(json.dumps({"step": "beats", "id": rid, "error": err}) + "\n")
    print(f"beats ok: {len(ok)}/{len(picked)}")

    summaries = [
        {
            "id": rid,
            "creator": rid.split("/")[0],
            "seconds": round(transcripts[rid].audio_duration_seconds or 0),
            "hook_type": rec["hook_type"],
            "beats": [[b["function"], b["word_share"], b["purpose"]] for b in rec["beats"]],
        }
        for rid, rec in ok.items()
    ]
    fs = cluster_frameworks(client, summaries)
    stats = framework_stats(fs, transcripts, ratios)
    (FRAMEWORKS_DIR / "pilot_frameworks.json").write_text(fs.model_dump_json(indent=1), encoding="utf-8")

    lines = ["# Pilot framework cards\n"]
    for f in fs.frameworks:
        s = stats[f.name]
        lines += [
            f"## {f.name}",
            f"{s['reels']} reels, {s['creators']} creators, ~{s['median_seconds']}s, ~{s['median_words']} words, median outlier {s['median_outlier']}",
            f"Suits: {f.suits_content}\n",
        ]
        lines += [f"{i}. **{fn}**: {note}" for i, (fn, note) in enumerate(zip(f.beat_pattern, f.beat_notes), 1)]
        lines.append("\nMembers:")
        for rid in f.reel_ids:
            rec = ok[rid]
            lines.append(f"- `{rid}` ({rec['hook_type']}): {rec['thesis']}")
        lines.append("")
    (FRAMEWORKS_DIR / "pilot_cards.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {FRAMEWORKS_DIR / 'pilot_cards.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
