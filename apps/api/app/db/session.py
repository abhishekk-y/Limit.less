from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from redis.asyncio import Redis
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True, pool_size=20, max_overflow=10)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
