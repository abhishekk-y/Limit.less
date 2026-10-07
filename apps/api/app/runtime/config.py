"""Explicit local defaults; production refuses development credentials."""

import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[4]


class RuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=os.getenv("SKILLSETU_ENV_FILE"))
    environment: str = "development"
    database_url: str = f"sqlite+aiosqlite:///{ROOT / '.local' / 'skillsetu.db'}"
    jwt_secret_key: str = "local-development-only-change-before-deployment-2026"
    vault_key: str = "local-vault-only-change-before-deployment-2026"
    demo_mode: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    access_minutes: int = 15
    refresh_days: int = 7
    local_auto_apply_enabled: bool = False
    automation_browser_channel: str = "msedge"
    adzuna_app_id: str = Field(default="", repr=False)
    adzuna_app_key: str = Field(default="", repr=False)
    adzuna_daily_call_limit: int = Field(default=15, ge=1, le=250)

    @model_validator(mode="after")
    def validate_production(self):
        # Hosted PostgreSQL providers supply a synchronous URL. The runtime
        # and migration engine both require the asyncpg driver.
        for prefix in ("postgres://", "postgresql://"):
            if self.database_url.startswith(prefix):
                self.database_url = "postgresql+asyncpg://" + self.database_url[len(prefix):]
                break
        if self.environment == "production":
            if self.demo_mode or not self.database_url.startswith("postgresql+"):
                raise ValueError("Production requires PostgreSQL and DEMO_MODE=false")
            if any(
                len(key) < 32 or key.startswith("local-") for key in (self.jwt_secret_key, self.vault_key)
            ):
                raise ValueError("Production requires independent strong JWT_SECRET_KEY and VAULT_KEY")
            if self.jwt_secret_key == self.vault_key or "*" in self.cors_origins:
                raise ValueError("Use separate secrets and explicit CORS origins")
        return self
