"""Pre-flight check: validate the Apify token and show what we can still spend.

Run before any scrape. Exits non-zero if the token is bad or the remaining
monthly credit is below MIN_REMAINING_BUDGET_USD.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reel_framework_library.apify_status import AccountCheckError, fetch_account_status  # noqa: E402
from reel_framework_library.config import MIN_REMAINING_BUDGET_USD, PROJECT_ROOT  # noqa: E402
from reel_framework_library.openai_status import check_openai  # noqa: E402


def main() -> int:
    """Print account status; return a process exit code."""
    load_dotenv(PROJECT_ROOT / ".env")
    token = os.environ.get("APIFY_API_KEY")
    if not token:
        print("FAIL: APIFY_API_KEY is not set (copy .env.example to .env)")
        return 1

    try:
        status = fetch_account_status(token)
    except AccountCheckError as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"Apify user:      {status.username}")
    print(f"Plan / tier:     {status.plan} / {status.tier}")
    print(f"Monthly cap:     ${status.monthly_cap_usd:.2f}")
    print(f"Spent so far:    ${status.spent_usd:.4f}")
    print(f"Remaining:       ${status.remaining_usd:.2f}")
    print(f"Price per reel:  ${status.price_per_reel_usd}")
    print(f"Price/profile:   ${status.price_per_profile_usd}")
    print(f"Run start fee:   ${status.start_fee_usd}")

    if status.remaining_usd < MIN_REMAINING_BUDGET_USD:
        print(f"FAIL: remaining budget is under ${MIN_REMAINING_BUDGET_USD:.2f}")
        return 1

    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("FAIL: OPENAI_API_KEY is not set (needed for transcription)")
        return 1
    try:
        print(f"OpenAI:          {check_openai(openai_key)}")
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
