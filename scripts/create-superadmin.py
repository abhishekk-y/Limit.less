"""Provision a platform superadmin locally; there is no public signup path for this role."""

import asyncio
import argparse
import getpass
import re
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.runtime.config import RuntimeSettings
from app.runtime.models import Account, Base, Workspace
from app.runtime.security import hash_password


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="")
    parser.add_argument("--email", default="")
    parser.add_argument("--generate-password", action="store_true")
    args = parser.parse_args()
    name = (args.name or input("Superadmin name: ")).strip()
    email = (args.email or input("Superadmin email: ")).strip().lower()
    password = secrets.token_urlsafe(24) if args.generate_password else getpass.getpass("New password (16+ characters): ")
    confirm = password if args.generate_password else getpass.getpass("Confirm password: ")
    if len(name) < 2 or len(name) > 160 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise SystemExit("Enter a valid name and email.")
    if len(password) < 16 or password != confirm:
        raise SystemExit("Passwords must match and contain at least 16 characters.")

    settings = RuntimeSettings()
    if settings.environment == "production":
        raise SystemExit("This bootstrap command is local-only. Provision production superadmins through your audited deployment process.")
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with sessions() as db:
            existing = await db.scalar(select(Account).where(Account.email == email))
            if existing:
                raise SystemExit("That email already has an account. This tool creates a new account only.")
            workspace = Workspace(name=f"{name} · Platform Operations", type="individual", plan="internal", is_demo=False)
            db.add(workspace)
            await db.flush()
            account = Account(
                tenant_id=workspace.id,
                email=email,
                name=name,
                password_hash=hash_password(password),
                role="superadmin",
                profile={"provisioned_by": "local superadmin setup"},
            )
            db.add(account)
            await db.commit()
            print(f"Created superadmin account for {email}. Password was stored as a hash and was not printed.")
            if args.generate_password:
                print(f"ONE_TIME_PASSWORD={password}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit("Cancelled.")
