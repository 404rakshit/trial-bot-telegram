"""Application Configuration"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List, Union


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Environment
    ENV: str = "development"  # development, staging, production
    DEBUG: bool = True

    # API Settings
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-secret-key-change-in-production"

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

    # Database
    DATABASE_URL: str = "postgresql://weather_user:weather_pass@postgres:5432/weather_bot"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_OTP_TTL: int = 600  # 10 minutes for OTP
    REDIS_WEATHER_CACHE_TTL: int = 3600  # 1 hour for weather data
    REDIS_SESSION_TTL: int = 86400  # 24 hours for session (refreshed on each request)

    # Session Authentication
    SESSION_HEADER_NAME: str = "X-Session-ID"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""  # e.g., https://your-domain.com/webhook/telegram

    # OpenWeatherMap
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # Celery (if using instead of APScheduler)
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Weather check interval (minutes)
    WEATHER_CHECK_INTERVAL: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
