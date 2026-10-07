from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/subscription")
async def get_subscription(db: AsyncSession = Depends(get_db)):
    return {"status": "active"}

@router.post("/pay")
async def process_payment(db: AsyncSession = Depends(get_db)):
    return {"status": "paid"}
