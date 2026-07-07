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

    # Databricks Zerobus Ingest Configuration (Phase 2)
    databricks_zerobus_endpoint: str = Field(
        default="", description="Zerobus endpoint (no https://)"
    )
    databricks_workspace_url: str = Field(
        default="", description="Databricks workspace URL (with https://)"
    )
    databricks_client_id: str = Field(
        default="", description="Service principal client ID for Zerobus"
    )
    databricks_client_secret: str = Field(
        default="", description="Service principal client secret for Zerobus"
    )

    # OpenAI Configuration (Additional)
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name")

    # Langfuse Configuration (Phase 2+)
    langfuse_public_key: str = Field(default="", description="Langfuse public key")
    langfuse_secret_key: str = Field(default="", description="Langfuse secret key")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", description="Langfuse host URL")

    # Legacy/Deprecated Fields (for backward compatibility)
    databricks_workspace_id: str = Field(default="", description="Deprecated: Workspace ID")
    databricks_region: str = Field(default="", description="Deprecated: Region")
    event_hubs_connection_string: str = Field(default="", description="Deprecated: Event Hubs connection")

    # Application Configuration
    environment: str = Field(default="development", description="Environment name")
    log_level: str = Field(default="INFO", description="Logging level")
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    cors_origins: str = Field(default="http://localhost:3000", description="CORS allowed origins (comma-separated)")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
