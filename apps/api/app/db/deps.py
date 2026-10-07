from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends
from app.db.session import AsyncSessionLocal
from app.core.exceptions import TenantAccessDenied

async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        # Enforce tenant context if present
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            await session.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")
        yield session
