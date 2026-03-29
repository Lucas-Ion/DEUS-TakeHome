"""
config.py provides the application configuration

Settings are loaded from environment variables.
In a prod app I would put them on the KeyVault or AWS Secrets Manager if on AWS
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    This is the central config for the API.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = Field(default="DEUS Logistics API")
    app_version: str = Field(default="1.0.0")
    app_description: str = Field(default="Vessel and cargo shipment management API")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    api_prefix: str = Field(default="/api/v1")
    database_url: str = Field(default="sqlite+aiosqlite:///./deus_logistics.db")
    log_level: str = Field(default="INFO")
    applicationinsights_connection_string: str | None = Field(default=None)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def app_insights_enabled(self) -> bool:
        return self.applicationinsights_connection_string is not None


@lru_cache
def get_settings() -> Settings:
    return Settings()
