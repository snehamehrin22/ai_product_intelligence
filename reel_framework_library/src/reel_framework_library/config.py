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
