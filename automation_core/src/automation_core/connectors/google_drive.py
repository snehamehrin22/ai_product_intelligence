from __future__ import annotations

from typing import Literal, Optional

from googleapiclient.discovery import build

from automation_core.auth.google import (
    get_google_service_account_credentials,
    get_google_user_credentials,
)
from automation_core.config import Settings, get_settings


DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service(
    *,
    auth_mode: Literal["user", "service_account"] = "user",
    settings: Optional[Settings] = None,
):
    s = settings or get_settings()
    if auth_mode == "service_account":
        creds = get_google_service_account_credentials(DRIVE_SCOPES, s)
    else:
        creds = get_google_user_credentials(DRIVE_SCOPES, s)
    return build("drive", "v3", credentials=creds, cache_discovery=False)

