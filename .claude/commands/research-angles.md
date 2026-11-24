---
description: Turn a raw observation into 10-15 evidence-informed research angles
argument-hint: "<observation>"
---

Observation: $ARGUMENTS

Run the three-stage research-angle pipeline. If the observation is empty, ask for one and stop.

1. Create `RUN_DIR = agents/research_agent/runs/<YYYY-MM-DD>-<short-slug>` and save the observation in `RUN_DIR/observation.txt`.
2. Run the `angle-researcher` subagent with the observation and RUN_DIR. Wait for it.
3. Run `angle-finder` with RUN_DIR. Wait.
4. Run `angle-generator` with RUN_DIR. Wait.
5. After each stage, run `python scripts/validate_stage.py <notes|findings|angles> RUN_DIR` from `agents/research_agent` (venv activated). If it fails, re-run that stage once with the error text; if it fails again, stop and report.
6. Finish by showing the contents of `RUN_DIR/angles.md`, plus the stats line from the angles validator (count, speculative, challenging). Stop there: no ranking, no recommendation of which angle to pursue.
