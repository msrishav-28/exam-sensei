"""
Configuration management for ExamSensei
Loads environment variables and provides typed configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Database
    database_url: str = "sqlite:///./examsensei.db"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Ollama
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    ollama_timeout: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@examsensei.com"
    
    # Scraping
    scraper_user_agent: str = "ExamSensei-Bot/1.0"
    scraper_delay: int = 2
    scraper_max_retries: int = 3
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/examsensei.log"
    
    # Environment
    environment: str = "development"
    
    # API
    api_version: str = "v1"
    api_prefix: str = "/api/v1"
    
    # Monitoring
    sentry_dsn: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
