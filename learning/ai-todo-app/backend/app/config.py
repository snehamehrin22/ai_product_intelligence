"""Configuration management using Pydantic Settings.

Loads environment variables from .env file and provides type-safe config access.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Databricks Configuration
    databricks_host: str = Field(..., description="Databricks workspace URL")
    databricks_token: str = Field(..., description="Databricks Personal Access Token")
    databricks_http_path: str = Field(..., description="SQL Warehouse HTTP path")
    databricks_catalog: str = Field(default="main", description="Unity Catalog name")
    databricks_schema: str = Field(default="todo_app", description="Schema name")

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Azure Event Hubs (Phase 2+)
    event_hubs_connection_string: str = Field(
        default="", description="Event Hubs connection string"
    )

    # Application Configuration
    environment: str = Field(default="development", description="Environment name")
    log_level: str = Field(default="INFO", description="Logging level")
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
