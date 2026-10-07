from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillSetu X"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["*"]
    
    DATABASE_URL: str
    REDIS_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    LLM_API_KEY: str = ""
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    SENTRY_DSN: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
