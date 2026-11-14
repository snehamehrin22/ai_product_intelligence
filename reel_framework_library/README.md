# Reel Framework Library

Builds a corpus of top-performing Instagram reels from creators I like, to extract script frameworks. See `docs/PRD.md`.

## Run

```bash
# 1. Create the environment (Python 3.13) and install
/usr/local/bin/python3.13 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 2. Add your key, then check the connection and remaining budget
cp .env.example .env   # fill in APIFY_API_KEY
python scripts/check_connections.py

# 3. Run the tests
python -m pytest
```

Rebuild the seed list after editing `data/seed/*.csv`: `python scripts/build_creators.py`
