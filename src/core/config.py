from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8700

    postgres_host: str = "postgres"
    postgres_port: int = 5700
    postgres_db: str = "privacyops"
    postgres_user: str = "pops"
    postgres_password: str = "pops"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    redis_host: str = "redis"
    redis_port: int = 6700
    redis_password: str = "change-me-redis-secret"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"

    ollama_base_url: str = "http://ollama:11700"
    ollama_chat_model: str = "qwen2.5:14b"

    paseto_secret_key: str = "replace-with-32-byte-secret-key!"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 14

    @field_validator("paseto_secret_key")
    @classmethod
    def _secret_min_length(cls, v: str) -> str:
        if len(v.encode()) < 32:
            raise ValueError("PASETO secret key must be at least 32 bytes")
        return v

    otel_exporter_otlp_endpoint: str = "http://tempo:4700"
    otel_service_name: str = "privacyops-api"
    enable_log_masking: bool = True

    cors_allow_origins: str = "http://localhost:3702,http://localhost:8700"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]

    default_dsr_sla_days: int = 30
    consent_expiry_warning_days: int = 30
    localization_strict_mode: bool = True
    processor_review_rejection_threshold: int = Field(default=80, ge=0, le=100)


def get_settings() -> Settings:
    return Settings()

settings: Settings = Settings()
