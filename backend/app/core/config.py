"""Application Configuration - Simplified for Local MVP"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List, Union


class Settings(BaseSettings):
    """Simplified application settings for local development"""

    # Environment
    ENV: str = "development"
    DEBUG: bool = True

    # API Settings
    API_V1_STR: str = "/api"

    # CORS - Can be a comma-separated string or list
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    # Database - SQLite for local MVP
    DATABASE_URL: str = "sqlite:///./reminders.db"

    # Session TTLs (seconds)
    OTP_TTL: int = 600  # 10 minutes
    SESSION_TTL: int = 86400  # 24 hours
    WEATHER_CACHE_TTL: int = 3600  # 1 hour for weather data

    # Session Authentication
    SESSION_HEADER_NAME: str = "X-Session-ID"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # OpenWeatherMap
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # Weather check interval (seconds)
    WEATHER_CHECK_INTERVAL: int = 900  # 15 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
