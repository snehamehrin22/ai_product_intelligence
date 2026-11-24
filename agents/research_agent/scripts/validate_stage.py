"""Validate a pipeline stage file and enforce cross-stage invariants.

Usage:
    python scripts/validate_stage.py notes    runs/<run_id>
    python scripts/validate_stage.py findings runs/<run_id>
    python scripts/validate_stage.py angles   runs/<run_id>

Exit code 0 = valid; non-zero prints what to fix.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pydantic import ValidationError  # noqa: E402

from research_agent.schemas import Angles, Findings, ResearchNotes  # noqa: E402


def load(run_dir: Path, name: str) -> dict:
    """Load a stage JSON file from the run directory."""
    return json.loads((run_dir / f"{name}.json").read_text(encoding="utf-8"))


def main() -> int:
    """Validate the requested stage; return process exit code."""
    stage, run_dir = sys.argv[1], Path(sys.argv[2])
    try:
        if stage == "notes":
            data = ResearchNotes(**load(run_dir, "notes"))
            print(f"OK: {len(data.notes)} notes")
        elif stage == "findings":
            data = Findings(**load(run_dir, "findings"))
            note_ids = {n.note_id for n in ResearchNotes(**load(run_dir, "notes")).notes}
            bad = [n for f in data.findings for n in f.note_ids if n not in note_ids]
            if bad:
                print(f"FAIL: findings cite unknown note_ids: {bad}")
                return 1
            print(f"OK: {len(data.findings)} findings")
        elif stage == "angles":
            data = Angles(**load(run_dir, "angles"))
            ids = {f.finding_id for f in Findings(**load(run_dir, "findings")).findings}
            bad = [a.angle for a in data.angles if a.finding_id not in ids]
            if bad:
                print(f"FAIL: angles cite unknown finding_ids: {bad}")
                return 1
            spec = sum(a.speculative for a in data.angles)
            chal = sum(a.challenges_assumption for a in data.angles)
            print(f"OK: {len(data.angles)} angles | speculative {spec} | challenge assumption {chal}")
        else:
            print(f"Unknown stage: {stage}")
            return 2
    except (ValidationError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"FAIL: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
