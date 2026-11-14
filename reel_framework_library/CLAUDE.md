# Reel Framework Library

Builds a corpus of top-performing Instagram reels from creators Sneha likes, so
script frameworks can be extracted from data. Spec: `docs/PRD.md`.

## Commands
```bash
source .venv/bin/activate
python scripts/check_connections.py   # run before any scrape; exits non-zero if token bad or budget < $1
python scripts/build_creators.py      # rebuild data/creators.csv from data/seed/*.csv
python -m pytest                      # no network needed
```

## Layout
- `src/reel_framework_library/`: logic only, no `main()`. `schemas.py` is the single source of truth.
- `scripts/`: entry points with `main()`.
- `data/creators.csv` and `data/seed/` are tracked. Everything else under `data/` is local run output.

## Bugs Found & Lessons Learned
Carried over from `instagram_hook_analyzer` (see PRD section 4).

| Problem | Root cause | Fix / lesson |
|---|---|---|
| `views` column empty | Code read `videoViewCount`, which Apify returns as None | Read `videoPlayCount`; fail loudly on null views |
| Couldn't rank reels from profile pulls | Profile scraper returns no views and mixes in carousels | Reel scraper for performance, profile scraper only for follower count |
| Hook scores didn't separate reels (all 70-90) | GPT scored its own labels | Rank by measured outlier ratio (views / creator median) only |
| Failed analyses saved as data | Fallback wrote `score=0` rows into the CSV | Failures go to `data/errors.jsonl`, never into the corpus |
| Raw run lost after 7 days | Apify dataset retention | Save raw JSON per creator as soon as a run finishes |
| Wrong env var name in a check (`APIFY_API_TOKEN`) | Assumed the name instead of reading `.env` | The variable is `APIFY_API_KEY` |
| Cost estimate wrong by 2x | Guessed the Starter plan price from memory | Read price and plan from the Apify API; `check_connections.py` does this |

## Conventions
- Handles are lowercase, no `@`. Clean them with `normalize_handle()` at import; `Creator` rejects anything dirty.
- Never hardcode per-reel prices; they vary by plan tier.
- Reel scraper charges $0.001 per run start: batch creators into one run.

## Data notes
- `chasehughesofficial` and `vvanedwards` were missing from a Notion view read but are real accounts (fetched OK).
- `isabelradford_` was dropped: the reel scraper returned nothing and the profile came back all-null.
