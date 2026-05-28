from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# One engine per process — creating multiple engines wastes connections.
engine = create_async_engine(settings.database_url, echo=False)

# async_sessionmaker is the async equivalent of sessionmaker.
# expire_on_commit=False: after commit, ORM objects stay usable
# (important for async — expired objects would trigger extra awaited queries).
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request."""
    async with AsyncSessionLocal() as session:
        yield session
