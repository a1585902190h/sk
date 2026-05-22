"""
Configuration module for Football Match Predictor
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings"""

    # FastAPI Configuration
    DEBUG: bool = Field(default=True, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_TITLE: str = Field(default="Football Match Predictor API", env="API_TITLE")
    API_VERSION: str = Field(default="1.0.0", env="API_VERSION")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/football_predictor",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")

    # MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    MONGODB_DATABASE: str = Field(default="football_predictor", env="MONGODB_DATABASE")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")

    # API Keys
    FOOTBALL_DATA_API_KEY: Optional[str] = Field(default=None, env="FOOTBALL_DATA_API_KEY")
    ESPN_API_KEY: Optional[str] = Field(default=None, env="ESPN_API_KEY")
    RAPIDAPI_KEY: Optional[str] = Field(default=None, env="RAPIDAPI_KEY")

    # Data Fetching
    DATA_FETCH_INTERVAL: int = Field(default=3600, env="DATA_FETCH_INTERVAL")
    DATA_SOURCES: str = Field(
        default="football_data,espn,rapidapi,web_scraper",
        env="DATA_SOURCES"
    )
    ENABLE_AUTO_UPDATE: bool = Field(default=True, env="ENABLE_AUTO_UPDATE")

    # Model Configuration
    DEFAULT_MODEL: str = Field(default="ensemble", env="DEFAULT_MODEL")
    MODELS_TO_USE: str = Field(
        default="elo,logistic_regression,random_forest,xgboost,lstm,ensemble",
        env="MODELS_TO_USE"
    )

    # Model Training
    TRAIN_INTERVAL: int = Field(default=604800, env="TRAIN_INTERVAL")
    TRAIN_TEST_SPLIT: float = Field(default=0.8, env="TRAIN_TEST_SPLIT")
    VALIDATION_SPLIT: float = Field(default=0.2, env="VALIDATION_SPLIT")
    RANDOM_STATE: int = Field(default=42, env="RANDOM_STATE")

    # Feature Engineering
    FEATURE_WINDOW_SIZE: int = Field(default=10, env="FEATURE_WINDOW_SIZE")
    INCLUDE_PLAYER_STATS: bool = Field(default=True, env="INCLUDE_PLAYER_STATS")
    INCLUDE_WEATHER_DATA: bool = Field(default=False, env="INCLUDE_WEATHER_DATA")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    ENABLE_SENTRY: bool = Field(default=False, env="ENABLE_SENTRY")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # CORS & Security
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5000",
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_METHODS: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        env="ALLOWED_METHODS"
    )
    ALLOWED_HEADERS: str = Field(default="*", env="ALLOWED_HEADERS")
    ENABLE_HTTPS: bool = Field(default=False, env="ENABLE_HTTPS")
    SECRET_KEY: str = Field(default="your_secret_key_here", env="SECRET_KEY")

    # Email Configuration
    SMTP_SERVER: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    ALERT_EMAIL: Optional[str] = Field(default=None, env="ALERT_EMAIL")
    ENABLE_EMAIL_ALERTS: bool = Field(default=False, env="ENABLE_EMAIL_ALERTS")

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")

    # Caching
    ENABLE_CACHE: bool = Field(default=True, env="ENABLE_CACHE")
    CACHE_BACKEND: str = Field(default="redis", env="CACHE_BACKEND")

    # Performance
    ENABLE_PROFILING: bool = Field(default=False, env="ENABLE_PROFILING")
    SLOW_QUERY_LOG_TIME: int = Field(default=1000, env="SLOW_QUERY_LOG_TIME")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def origins_list(self) -> list:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def models_list(self) -> list:
        """Parse MODELS_TO_USE into a list"""
        return [model.strip() for model in self.MODELS_TO_USE.split(",")]

    @property
    def data_sources_list(self) -> list:
        """Parse DATA_SOURCES into a list"""
        return [source.strip() for source in self.DATA_SOURCES.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export singleton instance
settings = get_settings()
