from functools import lru_cache
from typing import Any

from .config import Settings, settings


@lru_cache
def get_settings() -> Settings:
    """
    Returns the application's shared configuration.

    lru_cache ensures the same Settings instance is reused
    throughout the application process.
    """
    return settings


def get_agent_dependencies() -> dict[str, Any]:
    """
    Central dependency registry for the agent system.

    External services will be registered here as LEADFORGE
    grows. The orchestrator should receive dependencies through
    this boundary instead of constructing provider clients itself.
    """
    return {
        "settings": get_settings(),
    }
