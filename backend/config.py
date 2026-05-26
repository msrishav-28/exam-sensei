"""
Configuration management for ExamSensei.
Loads environment variables and provides typed configuration.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    # ---- Database ---------------------------------------------------------
    # SQLite locally for tests/dev; Supabase Postgres in prod.
    database_url: str = "sqlite:///./examsensei.db"

    # ---- Supabase Auth ----------------------------------------------------
    # Used by auth.py to verify Supabase-issued JWTs.
    supabase_url: str = ""
    supabase_jwt_secret: str = "dev-supabase-jwt-secret-change-in-production"
    supabase_anon_key: str = ""             # optional; for admin RPCs from backend
    supabase_service_role_key: str = ""     # optional; service-side ops only

    # ---- LLM providers ----------------------------------------------------
    # `llm_provider` = "auto" picks the first configured key in priority order:
    # anthropic > openai > groq > gemini > null (canned fallback).
    llm_provider: str = "auto"
    google_api_key: str = ""
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_request_timeout: int = 15

    # ---- CORS — comma-separated string parsed to list --------------------
    allowed_origins: str = (
        "http://localhost:3000,"
        "http://localhost:3001,"
        "https://exam-sensei.vercel.app"
    )

    def get_allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ---- Email (optional) -------------------------------------------------
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@examsensei.com"

    # ---- Scraping (read by backend/scripts/refresh_exam_data.py) ---------
    scraper_user_agent: str = "ExamSensei-Bot/1.0"
    scraper_delay: int = 2
    scraper_max_retries: int = 3

    # ---- Rate limiting on the few endpoints that still need it -----------
    chat_rate_limit: str = "30/minute"

    # ---- Logging ---------------------------------------------------------
    log_level: str = "INFO"
    log_file: str = "logs/examsensei.log"

    # ---- Environment -----------------------------------------------------
    environment: str = "development"

    # ---- API -------------------------------------------------------------
    api_version: str = "v1"
    api_prefix: str = "/api/v1"

    # ---- Monitoring ------------------------------------------------------
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


_DEFAULT_SUPABASE_JWT_SECRET = "dev-supabase-jwt-secret-change-in-production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings and enforce production invariants."""
    s = Settings()

    if s.environment == "production" and s.supabase_jwt_secret == _DEFAULT_SUPABASE_JWT_SECRET:
        raise RuntimeError(
            "SUPABASE_JWT_SECRET is still the default value in production. "
            "Set it from Supabase Dashboard → Settings → API → JWT Secret."
        )

    return s


# Global settings instance
settings = get_settings()
