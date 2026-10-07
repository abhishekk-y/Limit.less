"""Deployment settings must accept provider URLs without weakening validation."""
import pytest
from app.runtime.config import RuntimeSettings


@pytest.mark.parametrize("scheme", ["postgres://", "postgresql://", "postgresql+asyncpg://"])
def test_hosted_postgres_uses_async_driver(scheme):
    settings = RuntimeSettings(
        environment="production", demo_mode=False,
        database_url=scheme + "user:password@database:5432/limitless",
        jwt_secret_key="j" * 48, vault_key="v" * 48,
        cors_origins=["https://workspace.example.org"],
    )
    assert settings.database_url == "postgresql+asyncpg://user:password@database:5432/limitless"


def test_production_still_rejects_development_database():
    with pytest.raises(ValueError, match="Production requires PostgreSQL"):
        RuntimeSettings(environment="production", database_url="sqlite+aiosqlite:///:memory:")
