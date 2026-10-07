from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/")
async def list_applications(db: AsyncSession = Depends(get_db)):
    return []

@router.post("/")
async def create_application(db: AsyncSession = Depends(get_db)):
    return {"message": "created"}
