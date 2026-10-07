from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/")
async def list_opportunities(db: AsyncSession = Depends(get_db)):
    return []

@router.get("/{id}")
async def get_opportunity(id: str, db: AsyncSession = Depends(get_db)):
    return {"id": id}
