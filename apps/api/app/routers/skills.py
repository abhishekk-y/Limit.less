from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/")
async def list_skills(db: AsyncSession = Depends(get_db)):
    return []

@router.get("/{skill_id}")
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_db)):
    return {"id": skill_id}
