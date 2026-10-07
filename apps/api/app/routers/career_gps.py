from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/")
async def get_career_gps(db: AsyncSession = Depends(get_db)):
    return {"message": "career gps data"}
