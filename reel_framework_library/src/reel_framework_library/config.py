"""Project-wide settings. Plain constants so every script reads the same values."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CREATORS_CSV = DATA_DIR / "creators.csv"
NOTION_RAW_CSV = DATA_DIR / "seed" / "notion_raw.csv"
MANUAL_CREATORS_CSV = DATA_DIR / "seed" / "manual_creators.csv"

APIFY_API_BASE = "https://api.apify.com/v2"
REEL_ACTOR_ID = "apify~instagram-reel-scraper"
PROFILE_ACTOR_ID = "apify~instagram-profile-scraper"

# Fetch 3x what we keep: some reels will have no speech (see PRD US-4).
REELS_PER_CREATOR = 30

# Below this much remaining monthly credit, scripts refuse to proceed so a
# run can't die halfway and leave a creator half-saved.
MIN_REMAINING_BUDGET_USD = 1.00

RAW_DIR = DATA_DIR / "raw"
PROFILES_DIR = DATA_DIR / "profiles"
ERRORS_JSONL = DATA_DIR / "errors.jsonl"

# Creators per scraper run. Each run costs a flat start fee, so bigger batches
# are cheaper; but a run that dies loses its whole batch, so not too big.
BATCH_SIZE = 10

TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
SCORED_CSV = DATA_DIR / "reels_scored.csv"
TRANSCRIPTION_MODEL = "whisper-1"

# From memory of OpenAI's published price, not read from an API: check
# https://openai.com/api/pricing before a big run. Only used for the estimate
# and the --max-usd guard.
WHISPER_USD_PER_MINUTE = 0.006
TRANSCRIBE_WORKERS = 4

SELECTED_CSV = DATA_DIR / "selected_reels.csv"
SPEECH_CSV = DATA_DIR / "reels_speech.csv"
REELS_PER_CREATOR_SELECTED = 10

# "Has speech" thresholds, chosen from the real distribution (see PRD US-5):
# 1,001 of 1,357 reels run at 160+ words/min; a tail sits below 80. Whisper's own
# no_speech_prob wrongly discards real speech over background music, so it is
# not used for coverage.
MIN_SPEECH_COVERAGE = 0.70   # share of the video covered by transcript segments
MIN_WORDS = 40               # shorter than this is too little to learn structure from
MIN_WORDS_PER_MINUTE = 100   # below this it is sparse text or music, not narration

# Framework extraction pilot (see docs/PRD.md US-6/US-7). Small on purpose:
# find out whether frameworks exist before running on the whole corpus.
BEATS_DIR = DATA_DIR / "beats"
FRAMEWORKS_DIR = DATA_DIR / "frameworks"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
EXTRACTION_MODEL = "gpt-4o"
PILOT_CREATORS = 10
PILOT_REELS_PER_CREATOR = 4
