from functools import lru_cache
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, settings
from .database import get_db


@lru_cache
def get_settings() -> Settings:
    """
    Returns the application's shared configuration.

    The cached Settings instance provides a single configuration
    object throughout the application process.
    """

    return settings


async def get_database_session(
    session: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """
    FastAPI dependency that provides a database session.

    Routes should depend on this boundary rather than creating
    database sessions directly.
    """

    return session


def get_agent_dependencies() -> dict[str, Any]:
    """
    Central dependency registry for the agent system.

    Provider implementations should receive configuration and
    services through this boundary instead of constructing
    infrastructure dependencies inside the orchestrator.
    """

    return {
        "settings": get_settings(),
    }
