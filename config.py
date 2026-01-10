"""
Centralized configuration module for DocuRAG.

All environment variables are loaded and validated here. Import `settings` at
application startup to guarantee fail-fast validation before server boot.

Usage:
    from config import settings
    
    # Access typed settings
    db_uri = settings.MONGODB_URI
    if settings.is_production:
        ...
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation.
    
    Required fields (no defaults) will cause validation errors if missing.
    Optional fields have sensible defaults for local development.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # ==============================================
    # REQUIRED - App will fail to start without these
    # ==============================================
    
    MONGODB_URI: str
    JWT_SECRET_KEY: str
    OPENAI_API_KEY: str
    DEEPSEEK_API_KEY: str
    
    # Storage (R2/S3)
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_ENDPOINT: str
    R2_BUCKET_NAME: str
    
    # ==============================================
    # OPTIONAL - Have sensible defaults
    # ==============================================
    
    # Environment
    ENVIRONMENT: str = "development"
    MONGODB_DATABASE: str = "docurag"
    
    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    APP_URL: str = "http://localhost:5173"
    
    # JWT Settings
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Cookie Settings
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: Optional[str] = None
    
    # Storage Provider
    STORAGE_PROVIDER: str = "r2"
    AWS_REGION: str = "us-east-1"
    
    # AWS S3 (alternative to R2)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    
    # Google OAuth (optional)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # Email Service (optional)
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "DocuRAG <onboarding@resend.dev>"
    APP_NAME: str = "Querious"
    
    # ==============================================
    # COMPUTED PROPERTIES
    # ==============================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins based on environment."""
        if self.is_production:
            return [self.FRONTEND_URL]
        return ["*"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    Validation happens on first call.
    """
    return Settings()


# Fail-fast: validate settings immediately on import
# This ensures the app won't start if required env vars are missing
settings = get_settings()
