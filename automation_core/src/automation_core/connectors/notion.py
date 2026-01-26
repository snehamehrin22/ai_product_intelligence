from __future__ import annotations

from typing import Optional

from notion_client import Client

from automation_core.config import Settings, get_settings


def get_notion_client(settings: Optional[Settings] = None) -> Client:
    s = settings or get_settings()
    if not s.notion_api_key:
        raise ValueError("Missing NOTION_API_KEY.")
    return Client(auth=s.notion_api_key)

