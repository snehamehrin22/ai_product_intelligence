from __future__ import annotations

import argparse
import sys

from automation_core.auth.google import get_google_user_credentials
from automation_core.config import get_settings


def _cmd_google_login(_: argparse.Namespace) -> int:
    s = get_settings()
    # Minimal scopes; expand per project as needed.
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    _ = get_google_user_credentials(scopes, s)
    print(f"Saved Google OAuth token to: {s.google_oauth_token_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="automation-core")
    sub = parser.add_subparsers(dest="cmd", required=True)

    google_login = sub.add_parser("google-login", help="Run Google OAuth installed-app flow and cache token")
    google_login.set_defaults(func=_cmd_google_login)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

