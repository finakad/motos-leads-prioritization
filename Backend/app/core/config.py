from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Motos Leads Prioritization API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/"
        "motos_leads_prioritization"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()