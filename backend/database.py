from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """
    Base class for all LEADFORGE SQLAlchemy database models.
    """

    pass


engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session to FastAPI routes.

    If an exception occurs while the session is being used,
    the active transaction is rolled back before the exception
    is re-raised.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def create_database_tables() -> None:
    """
    Creates all registered database tables.

    This helper is intended for development and controlled
    environments. Production schema changes should eventually
    be managed through Alembic migrations.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """
    Cleanly disposes of the database connection pool.

    This can be called during application shutdown.
    """

    await engine.dispose()
