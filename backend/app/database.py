"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.models import Base
from app.config import settings
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the absolute path to the backend directory
backend_dir = Path(__file__).parent.parent
db_path = backend_dir / "tictactoe.db"

# Build the database URL with absolute path
if "sqlite" in settings.DATABASE_URL:
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
else:
    DATABASE_URL = settings.DATABASE_URL

# Debug: Print the DATABASE_URL being used
print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")
print(f"DEBUG: Database file will be at: {db_path}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
