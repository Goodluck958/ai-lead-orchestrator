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
    Base class for all LEADFORGE database models.
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
    """

    async with AsyncSessionLocal() as session:
        yield session


async def create_database_tables() -> None:
    """
    Creates database tables registered with SQLAlchemy metadata.

    Development helper. Production deployments should use
    migrations rather than relying on automatic table creation.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
