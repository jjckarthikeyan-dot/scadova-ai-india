import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    PRODUCT_NAME: str = "Scadova-AI-India"
    MODULE_NAME: str = "loan_agency"
    API_VERSION: str = "1.0.0"

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="https://mock-supabase.supabase.co")
    SUPABASE_KEY: str = Field(default="mock-supabase-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="mock-supabase-service-role-key")
    STORAGE_BUCKET: str = Field(default="loan-agency-documents")

    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./scadova_india.db")
    SYNC_DATABASE_URL: str = Field(default="sqlite:///./scadova_india.db")

    # JWT Security
    JWT_SECRET_KEY: str = Field(default="development-secret-key-change-in-production-min32chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # AI Integration (Optional)
    AI_PROVIDER: str = "google"
    AI_MODEL: str = "gemini-1.5-pro"
    AI_API_KEY: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
