from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_db)):
    return {"message": "Current user"}

@router.patch("/me")
async def update_me(db: AsyncSession = Depends(get_db)):
    return {"message": "Updated user"}

@router.get("/{id}")
async def get_user_by_id(id: str, db: AsyncSession = Depends(get_db)):
    return {"message": f"User {id}"}

@router.delete("/me")
async def delete_me(db: AsyncSession = Depends(get_db)):
    return {"message": "Deleted user"}
