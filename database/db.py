from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory for async transactions
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

async def init_db():
    """Initializes the database by creating all defined models"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
