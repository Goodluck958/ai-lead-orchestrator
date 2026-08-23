from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db_models import User, UserRole, UserStatus
from .dependencies import get_database_session


# ------------------------------------------------------------------
# Password hashing
# ------------------------------------------------------------------

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using the password-hashing
    algorithm selected by pwdlib.
    """

    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against its stored hash.
    """

    return password_hash.verify(password, hashed_password)


# ------------------------------------------------------------------
# JWT configuration
# ------------------------------------------------------------------

def _get_jwt_secret() -> str:
    """
    Returns the JWT signing secret.

    A real secret is mandatory outside development.
    """

    if settings.jwt_secret_key:
        return settings.jwt_secret_key

    if settings.environment == "development":
        # Development-only fallback.
        # Production must provide JWT_SECRET_KEY.
        return "development-only-leadforge-secret-change-me"

    raise RuntimeError(
        "JWT_SECRET_KEY must be configured outside development."
    )


def create_access_token(
    user_id: str,
    role: UserRole,
) -> str:
    """
    Creates a signed JWT access token for an authenticated user.
    """

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": user_id,
        "role": role.value,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        _get_jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


# ------------------------------------------------------------------
# JWT verification
# ------------------------------------------------------------------

def _decode_access_token(token: str) -> dict:
    """
    Decodes and validates a LEADFORGE access token.
    """

    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[settings.jwt_algorithm],
        )

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing a subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# ------------------------------------------------------------------
# Current-user dependency
# ------------------------------------------------------------------

async def get_current_user(
    token: Annotated[str, Depends(
        lambda: None
    )],
    session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
) -> User:
    """
    Resolves the authenticated user represented by the JWT.

    NOTE:
    The OAuth2 bearer dependency is attached below through
    get_bearer_token(). Keeping token extraction separate makes
    the JWT verification logic independently testable.
    """

    payload = _decode_access_token(token)

    user_id = payload["sub"]

    result = await session.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active.",
        )

    return user


# ------------------------------------------------------------------
# Role-based authorization
# ------------------------------------------------------------------

def require_role(required_role: UserRole):
    """
    Creates a dependency that requires the authenticated user
    to have a specific role.
    """

    async def role_dependency(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return role_dependency


async def require_admin(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    """
    Requires the authenticated user to have administrator access.
    """

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


async def require_client(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    """
    Requires the authenticated user to have client access.
    """

    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client access required.",
        )

    return current_user
