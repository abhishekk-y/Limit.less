from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.post("/upload")
async def upload_document(db: AsyncSession = Depends(get_db)):
    return {"message": "uploaded"}

@router.get("/")
async def list_documents(db: AsyncSession = Depends(get_db)):
    return []
