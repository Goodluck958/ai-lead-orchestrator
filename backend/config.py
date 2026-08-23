import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Central application configuration.

    Secrets and environment-specific values are loaded from
    environment variables rather than being hard-coded.
    """

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    app_name: str = "LEADFORGE"
    app_version: str = "1.0.0"

    environment: str = Field(
        default_factory=lambda: os.getenv(
            "ENVIRONMENT",
            "development",
        )
    )

    # ---------------------------------------------------------
    # AI / Research Providers
    # ---------------------------------------------------------

    openai_api_key: str = Field(
        default_factory=lambda: os.getenv(
            "OPENAI_API_KEY",
            "",
        )
    )

    tavily_api_key: str = Field(
        default_factory=lambda: os.getenv(
            "TAVILY_API_KEY",
            "",
        )
    )

    # ---------------------------------------------------------
    # External Integrations
    # ---------------------------------------------------------

    google_credentials_json: str = Field(
        default_factory=lambda: os.getenv(
            "GOOGLE_CREDENTIALS_JSON",
            "",
        )
    )

    resend_api_key: str = Field(
        default_factory=lambda: os.getenv(
            "RESEND_API_KEY",
            "",
        )
    )

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/leadforge",
        )
    )

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------

    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY",
            "",
        )
    )

    jwt_algorithm: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_ALGORITHM",
            "HS256",
        )
    )

    access_token_expire_minutes: int = Field(
        default_factory=lambda: int(
            os.getenv(
                "ACCESS_TOKEN_EXPIRE_MINUTES",
                "60",
            )
        )
    )

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------

    api_prefix: str = "/api/v1"

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    cors_origins: list[str] = Field(
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
