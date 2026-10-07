from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(db: AsyncSession = Depends(get_db)):
    return {"message": "Register endpoint"}

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return {"message": "Login endpoint"}

@router.post("/google")
async def google_auth():
    return {"message": "Google auth"}

@router.post("/refresh")
async def refresh_token():
    return {"message": "Refresh token"}

@router.post("/logout")
async def logout():
    return {"message": "Logout"}

@router.post("/send-otp")
async def send_otp():
    return {"message": "OTP sent"}
