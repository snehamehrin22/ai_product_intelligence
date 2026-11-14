# PRD: Reel Framework Library

Status: draft v1 · Owner: Sneha · Storage: local only (no Notion write for now)

## 1. Problem

Turning my ideas into Instagram reel scripts is the bottleneck. I want to learn
from creators I already like, using real performance data, instead of guessing
at structure. The first analyzer (`instagram_hook_analyzer`) couldn't answer
"what works": 92 reels, views missing for 4 of 5 creators, and GPT-assigned
hook scores that ranged only 70-90.

## 2. Goal

Build a corpus of **top-performing reels that have speech** from the creators I
like, with transcripts and timing, so frameworks can be extracted from the
data. Frameworks themselves are a later phase; this PRD builds the corpus first.

### Non-goals (for now)
- Writing scripts / a generator
- Writing to Notion
- GPT "hook scores" (replaced by measured performance)
- Reels with no speech (silent montages, music-only, carousels)
- Filtering by format: talking head vs voiceover over footage are both kept and
  labelled later (US-5)

## 3. Inputs and constraints

**Creator list** (51 to start): the 47 creators in Notion "Instagram Reference"
(my saved collections) plus 4 added by hand: `eyes_of_apoorva`,
`andrea_mizrahi`, `iliya.sharifat`, `mi.raga_mi.saga`. Full list in Appendix A.
Target is 100; the other 49 are found later (US-8).

**Per creator:** 10 reels that (a) have speech in them (a talking head or a voiceover both
count) and (b) are performing well.

**"Performing well"** = `outlier_ratio = views / creator_median_views`, computed
over all reels fetched for that creator (before the speech filter, so the
median isn't biased). Raw views alone favour big accounts. Ranking uses outlier
ratio; raw views are kept for reference.

**Fetch size:** 30 reels per creator. The scraper returns recent reels, not the
all-time top, and some will have no speech, so we fetch 3x what
we keep.

**Budget:** Apify Starter plan (upgraded 2026-11-14): $19/month credit and
cap, BRONZE tier pricing of $0.0023/reel (confirmed via the Apify API; the
$19 figure replaces my earlier $39 guess). Profile scraper is priced the same
way and should be re-checked before the run.

| Scope | Reels | Approx. cost |
|---|---|---|
| 51 seed creators x 30 | 1,530 | ~$3.5 + ~$0.12 profiles (actual: ~$3.41 for 51) |
| 100 creators x 30 | 3,000 | ~$6.9 + ~$0.23 profiles |

Whisper (OpenAI) for ~1,000 selected reels is a separate cost, roughly $9
(estimate, not re-checked). Apify keeps datasets only 7 days, so every run
saves to disk immediately.

## 4. Lessons carried over from the first analyzer

| Problem | Cause | Rule now |
|---|---|---|
| `views` empty in the CSV | Code read `videoViewCount` (None); the populated field is `videoPlayCount` | Read `videoPlayCount`; fail loudly if views are null for a reel |
| Can't rank reels from profile pulls | Profile scraper returns no views and mixes carousels | Use the reel scraper for performance data; profile scraper only for follower count |
| Scores didn't separate reels | GPT scored its own labels | Rank by measured outlier ratio only |
| Failed analyses saved as data | Fallback wrote `score=0` rows | Failed rows go to an errors file, never into the corpus |
| Raw run lost after 7 days | Apify retention | Save raw JSON per creator the moment a run finishes |

## 5. User stories

Stories 2-5 are scoped now and detailed when the story before them is done.
Stories 6+ are placeholders until the corpus exists.

### US-1: Project setup (first story, detailed)

As the owner, I want a working project skeleton with validated connections and
a clean creator list, so every later story starts from known-good state.

Acceptance criteria:
1. Project at `ai_product_intelligence/reel_framework_library/` with `src/reel_framework_library/`
   (`schemas.py`, `config.py`), `scripts/`, `prompts/`, `tests/inputs/`, `data/`
   (gitignored), `docs/`.
2. Python 3.13 venv at `.venv` (`/usr/local/bin/python3.13 -m venv .venv`);
   `requirements.txt` lists only what is used so far.
3. `.env.example` documents `APIFY_API_KEY`; `.env` and `.venv/`, `data/`,
   `logs/`, `__pycache__/` are in `.gitignore`.
4. `scripts/check_connections.py` calls the Apify API and prints: username,
   plan, monthly cap, spent so far, remaining. It never prints the key. It
   exits non-zero if the token is invalid or remaining budget is under $1.00.
   It also reads the live per-reel price for the account's tier from the actor
   listing, so cost estimates never use a hardcoded price.
5. `data/creators.csv` holds the 51 creators from Appendix A with columns
   `handle, source, notion_category, notes`. Handles are lowercase, with no
   `@`, spaces or parentheses, and unique.
6. `schemas.py` has a Pydantic `Creator` model; a loader reads the CSV through
   it and raises on any invalid row.
7. `tests/inputs/` has sample creator files covering: `@` prefix, trailing
   whitespace, `name (display name)` format, duplicate handle across
   categories, empty handle, uppercase. `pytest` passes against them.
8. Project `CLAUDE.md` created with a "Bugs Found & Lessons Learned" section
   seeded from Section 4.
9. README has the three commands to run: create venv, check connections, run tests.

Done when: `pytest` is green, `check_connections.py` exits 0, and
`creators.csv` loads 51 valid rows.

### US-2: Fetch reels
As the owner, I want the reel scraper run for every creator with a cost
estimate shown first, so I never overspend the cap.
- `reels_per_creator` defaults to 30 (set in `config.py`).
- Shows estimated cost (`creators × reels_per_creator × price`) and stops if it
  would pass the remaining budget.
- Saves raw JSON per creator to `data/raw/{handle}.json` as each finishes;
  re-running skips creators already saved.
- Skips pinned reels and trial reels, so the window is the creator's 30 most
  recent regular reels.
- Creators go to the scraper in batches of 10 (one start fee per batch).
- Fails loudly on null views; writes failures to `data/errors.jsonl`.
- Also records follower count (profile scraper) for context.

### US-3: Score performance
- Per creator: median views, then `outlier_ratio` for each reel.
- **Recency caveat (found in the real data):** the 30-reel window includes reels
  posted in the last few days, still gaining views. Scoring them against the
  median makes them look like failures. Decide the rule before scoring: either
  exclude reels younger than N days (start with 7) from selection, or compare
  views per day since posting. Check what the data says before picking.
- Output `data/reels_scored.csv`; sanity check that no creator has all-null views.

### US-4: Transcribe every reel
Decided: transcribe all fetched reels (about 1,370, 1,484 minutes of audio,
about $8.90 at Whisper's $0.006/min, price from memory and not verified), with
no analysis yet. Selecting the top 10 per creator, and any speech-coverage
filter, move to a later story that works from the saved transcripts.
- Source is each reel's `audioUrl` from the raw scraper files (about 1 MB, vs
  25 MB+ for video). Instagram CDN links expire within days, so this runs soon
  after the fetch.
- Whisper `verbose_json`: text plus timed segments, each with `no_speech_prob`,
  so later steps can measure how much of a reel is speech.
- One validated file per reel: `data/transcripts/{handle}/{shortcode}.json`.
- Order: highest outlier ratio first, too-new reels last, so an interrupted run
  has finished the most useful reels.
- Resumable (saved reels are skipped); failures go to `data/errors.jsonl` and
  never stop the run.
- Cost guard: estimate shown first, refuses above `--max-usd` (default $10).

### US-5: Select top reels and label formats
- Select the top 10 per creator from the transcripts (speech-coverage rule and
  ranking method to be decided: rank within creator, or capped ratio).
- Label each selected reel's format (for example: talking head, voiceover over
  footage, text-on-screen with voiceover, interview) from the transcript plus
  sampled frames. The label set is decided from what the first creators'
  reels look like, not fixed in advance.
- Labels are a column used in the framework analysis, not a filter.

### Later (not scoped)
- US-6 Beat extraction with a fixed vocabulary, validated against hand labels
- US-7 Framework clustering, using the format label to compare frameworks within
  and across formats
- US-8 Find creators 53-100
- Deferred: on-screen text. The old Tesseract OCR was noisy (e.g. `an ale nner
  acome a4 +SsSo`) and it is the only step needing the videos. If hooks turn
  out to matter and transcripts miss them, revisit using a vision model on a
  few frames from the first 3 seconds, not Tesseract.

## 6. Decisions and open questions

Decided:
- Fetch **30 reels per creator**; Apify upgraded to Starter.
- "Talking head" means the reel has speech. Voiceover counts. Format is labelled
  later (US-5) and is not a filter.
- Mostly-montage accounts stay on the list; if they have few reels with speech
  they simply contribute fewer than 10.

Still open:
1. **Speech coverage threshold** (starting at 70% of the video's duration).
   Checked against real output on the first few creators.
2. **Budget for Whisper** (about $9 for 1,000 reels at my earlier estimate, not
   re-checked). OK to spend that from your OpenAI account?

## Appendix A: creator seed list (51)

Added by hand (4): eyes_of_apoorva, andrea_mizrahi, iliya.sharifat, mi.raga_mi.saga

From Notion "Instagram Reference" (47, handles normalized):

- Business Audit Styles: thoughtfully_designed, storieswithkiki, trythissj,
  aevytvdaily, bobbyinspace, byalisonwang, carmscrolls, eugbrandstrat,
  jade.got.curious, jason_swet, jeyessays, jun_yuh,
  mikayla.deg, mindfulnesswithdesiree, naomi.huth, reidseddon,
  sincerelyjennifergrace, synsation_, telephonepyar, travelingtoretirement,
  wellbysabzi
- City and Culture: alvinzhuxiyao, amdshutter, vanessapiccs, aksscameraroll
- Personal Essence: bymiilan, deathtostock, host___office, karocrafts,
  mariah_mpls, nathanmichael, philipp_goetze, scribbledbysophie, sreyahalder,
  steffygonzalezc, trevorgetsholistic, casey.carrl, edendotso, hellocherrymedia,
  inzeenius
- AI Teaching: nataliefratto, nick_saraev, uiuxmanuel, byaditimishra,
  chasehughesofficial, prajplays, vvanedwards

`isabelradford_` was dropped after the fetch (account returned no reels and an empty profile).

Creators appearing in two categories (`jason_swet`, `sincerelyjennifergrace`,
`eugbrandstrat`) are listed once.
