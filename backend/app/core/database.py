from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from ..models.models import Base

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for debugging
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)

# Create async session
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()