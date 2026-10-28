from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SKYCAST_")

    app_name: str = "Skycast"
    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url: str = "https://api.open-meteo.com/v1/forecast"
    language: str = "en"
    http_timeout: float = 10.0
    database_url: str = "sqlite:///./skycast.db"
    cache_ttl_seconds: int = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()
