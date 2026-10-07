from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/")
async def get_talent_twin_data(db: AsyncSession = Depends(get_db)):
    return {"message": "talent twin data"}
