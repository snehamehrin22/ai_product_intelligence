from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> Path:
    # Shared location across projects (laptop + server)
    # macOS/Linux: ~/.config/automation_core
    # If you want XDG compliance for Linux, this is already OK.
    return Path.home() / ".config" / "automation_core"


class Settings(BaseSettings):
    """
    Shared configuration for all automation projects.

    Loading order:
    - environment variables
    - optional .env (project-local)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_env: str = Field(default="local", validation_alias="APP_ENV")
    data_dir: Path = Field(default_factory=_default_data_dir, validation_alias="AUTOMATION_DATA_DIR")

    # Notion
    notion_api_key: Optional[str] = Field(default=None, validation_alias="NOTION_API_KEY")

    # Google (OAuth installed app)
    # Default location if you want to keep things simple:
    #   ~/.config/automation_core/google/client_secret.json
    google_oauth_client_secrets: Path = Field(
        default_factory=lambda: _default_data_dir() / "google" / "client_secret.json",
        validation_alias="GOOGLE_OAUTH_CLIENT_SECRETS",
    )
    google_oauth_token_path: Path = Field(
        default_factory=lambda: _default_data_dir() / "google" / "token.json",
        validation_alias="GOOGLE_OAUTH_TOKEN_PATH",
    )

    # Google (service account) – recommended for servers
    # Default location if you want to keep things simple:
    #   ~/.config/automation_core/google/service_account.json
    google_service_account_json: Path = Field(
        default_factory=lambda: _default_data_dir() / "google" / "service_account.json",
        validation_alias="GOOGLE_SERVICE_ACCOUNT_JSON",
    )

    def ensure_dirs(self) -> None:
        (self.data_dir / "google").mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s

