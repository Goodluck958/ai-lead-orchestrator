import os
from typing import List

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Central application configuration.

    Secrets are loaded from environment variables rather than
    being hard-coded into the source code.
    """

    app_name: str = "LEADFORGE"
    app_version: str = "1.0.0"
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )

    # AI / research providers
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    tavily_api_key: str = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY", "")
    )

    # Future external integrations used by LEADFORGE
    google_credentials_json: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    )
    resend_api_key: str = Field(
        default_factory=lambda: os.getenv("RESEND_API_KEY", "")
    )

    # API configuration
    api_prefix: str = "/api/v1"

    # CORS configuration
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:5173",
            ).split(",")
            if origin.strip()
        ]
    )


settings = Settings()
