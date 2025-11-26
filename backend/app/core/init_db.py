from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .database import engine
from ..models.models import Base

async def init_db():
    """Initialize the database with all tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Create indexes for better performance
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_category ON service_requests(category);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_priority ON service_requests(priority);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_created_at ON service_requests(created_at DESC);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_citizen_id ON service_requests(citizen_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_attachments_request_id ON attachments(request_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_comments_request_id ON comments(request_id);
        """))
        await conn.commit()

async def drop_db():
    """Drop all tables (for development/testing)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)