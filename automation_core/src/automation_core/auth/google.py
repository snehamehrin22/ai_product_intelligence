from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from google.auth.credentials import Credentials
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from automation_core.config import Settings, get_settings


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_google_service_account_credentials(
    scopes: Iterable[str],
    settings: Optional[Settings] = None,
) -> Credentials:
    """
    Server-friendly auth: uses a service account JSON.
    Set GOOGLE_SERVICE_ACCOUNT_JSON (or GOOGLE_APPLICATION_CREDENTIALS externally).
    """
    s = settings or get_settings()
    if not s.google_service_account_json or not s.google_service_account_json.exists():
        raise ValueError(
            "Missing service account JSON. Put it at "
            f"'{s.google_service_account_json}' or set GOOGLE_SERVICE_ACCOUNT_JSON."
        )

    return service_account.Credentials.from_service_account_file(
        filename=str(s.google_service_account_json),
        scopes=list(scopes),
    )


def get_google_user_credentials(
    scopes: Iterable[str],
    settings: Optional[Settings] = None,
) -> Credentials:
    """
    Laptop-friendly auth: OAuth installed app flow with token cache.
    Requires GOOGLE_OAUTH_CLIENT_SECRETS pointing to your client_secret.json.
    """
    s = settings or get_settings()
    if not s.google_oauth_client_secrets or not s.google_oauth_client_secrets.exists():
        raise ValueError(
            "Missing OAuth client secrets JSON. Put it at "
            f"'{s.google_oauth_client_secrets}' or set GOOGLE_OAUTH_CLIENT_SECRETS."
        )

    token_path = s.google_oauth_token_path
    _ensure_parent(token_path)

    creds: Optional[UserCredentials] = None
    if token_path.exists():
        creds = UserCredentials.from_authorized_user_file(str(token_path), list(scopes))

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(s.google_oauth_client_secrets), list(scopes))
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds

