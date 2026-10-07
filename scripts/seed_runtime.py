"""Idempotently seed clearly fictional demo accounts; never runs in production."""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.runtime.config import RuntimeSettings
from app.runtime.models import Account, Base, Workspace
from app.runtime.security import hash_password

DEMO_PASSWORD = "SkillSetu-Demo-2026!"
PERSONAS = [
    ("learner@skillsetu.demo", "Asha Sharma", "individual", "professional"),
    ("returner@skillsetu.demo", "Meera Kapoor", "individual", "professional"),
    ("graduate@skillsetu.demo", "Arjun Singh", "individual", "professional"),
    ("team@skillsetu.demo", "Demo Workforce", "organization", "org_admin"),
    ("campus@skillsetu.demo", "Demo Campus", "institution", "institution_admin"),
]


async def main():
    settings = RuntimeSettings()
    if not settings.demo_mode or settings.environment == "production":
        raise SystemExit("Demo seeding is disabled outside demo mode")
    (ROOT / ".local").mkdir(exist_ok=True)
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as db:
        for email, name, kind, role in PERSONAS:
            if await db.scalar(select(Account).where(Account.email == email)):
                continue
            workspace = Workspace(name=name, type=kind, is_demo=True)
            db.add(workspace)
            await db.flush()
            db.add(Account(email=email, name=name, tenant_id=workspace.id, role=role,
                password_hash=hash_password(DEMO_PASSWORD), profile={"consent": True, "age": 25, "target_role": "software-engineer"}))
        await db.commit()
    await engine.dispose()
    print("Five DEMO accounts are ready. Catalog: 96 fictional opportunities, 24 demo skills, 6 roles.")
    print("Emails: learner@skillsetu.demo / team@skillsetu.demo / campus@skillsetu.demo")
    print(f"Local demo password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
