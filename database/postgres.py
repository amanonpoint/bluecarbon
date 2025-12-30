# database/postgres.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:bcarbon123@localhost:5432/blue_carbon_db"
)

# For synchronous operations (like table creation)
SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    # Use psycopg2 for synchronous connections
    "postgresql+psycopg2://postgres:bcarbon123@localhost:5432/blue_carbon_db"
)

# Create async engine for FastAPI
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Create sync engine for migrations/init scripts
# Use connect_args to avoid SSL warnings if needed
sync_engine = create_engine(
    SYNC_DATABASE_URL, 
    echo=False,
    # Optional: For better connection handling
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factories
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@asynccontextmanager
async def get_async_session():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# For synchronous operations (e.g., init scripts)
def get_sync_session():
    from sqlalchemy.orm import Session
    with Session(sync_engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# Database initialization function
def init_db():
    """Initialize database tables"""
    from schemas.chat_models import Base
    print("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database tables created successfully!")