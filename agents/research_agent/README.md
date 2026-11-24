# Research Angle Engine

Claude Code does the research. Observation in, 10-15 evidence-informed research angles out.

```
/research-angles "<observation>"
```

Pipeline (subagents live in repo-root `.claude/agents/`, command in `.claude/commands/`):

1. `angle-researcher` — web research → `runs/<id>/notes.json`
2. `angle-finder` — 5-8 surprising findings → `findings.json`
3. `angle-generator` — 10-15 angles → `angles.json` + `angles.md`

`scripts/validate_stage.py` validates each stage with Pydantic and checks that every finding cites real notes and every angle cites a real finding. Run Claude Code from the repo root.

Scope ends at angle generation: no ranking, briefs, or content.
