"""
Supabase Auth integration.

The Supabase JS SDK on the frontend handles signup, login, password reset,
OAuth, magic links, MFA and refresh-token rotation. The backend's only job
is to verify the JWT it receives in the Authorization header on every
request and to look up the matching `users` row.

The auto-create of the `users` row from `auth.users` is done by the Postgres
trigger in `backend/migrations/001_supabase_profile_trigger.sql`.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User


_AUDIENCE = "authenticated"  # Supabase issues this aud claim for logged-in users
_ALGORITHM = "HS256"


def _unauthorized(detail: str = "Authentication required") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"message": detail, "details": {}},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_bearer(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Missing or malformed Authorization header")
    return authorization[7:].strip()


def _decode_supabase_jwt(token: str) -> dict:
    """Verify a Supabase-issued JWT and return its payload."""
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[_ALGORITHM],
            audience=_AUDIENCE,
        )
    except JWTError:
        raise _unauthorized("Invalid or expired token")


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: verify Supabase JWT and load the matching User row."""
    payload = _decode_supabase_jwt(_extract_bearer(authorization))

    sub = payload.get("sub")
    if not sub:
        raise _unauthorized("Token missing subject")

    try:
        user_uuid = UUID(str(sub))
    except (TypeError, ValueError):
        raise _unauthorized("Invalid user identifier in token")

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        # Profile row should be auto-created by the Supabase trigger. If it's
        # missing, the trigger isn't installed or something else is off —
        # surface as 401 so the frontend doesn't loop on stale sessions.
        raise _unauthorized("User profile not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """FastAPI dependency: same as get_current_user + is_active check."""
    if current_user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Inactive user", "details": {}},
        )
    return current_user
