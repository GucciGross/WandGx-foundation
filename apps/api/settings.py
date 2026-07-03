from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hermes Agent Starter"
    environment: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    next_public_api_url: str = "http://localhost:8000"
    database_url: str = "sqlite:///./.local/hermes.db"
    redis_url: str = "redis://localhost:6379/0"
    hermes_mode: str = "dormant"
    hermes_autofix: str = "pr_only"
    public_demo_mode: bool = True
    require_human_approval: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
