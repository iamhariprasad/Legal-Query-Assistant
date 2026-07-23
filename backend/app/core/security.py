"""Password hashing and JWT helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return whether a plain password matches a stored hash."""
    return bool(pwd_context.verify(plain_password, hashed_password))


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return str(pwd_context.hash(password))


def create_access_token(subject: str, settings: Settings) -> str:
    """Create a signed JWT access token."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    return str(jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM))


def decode_access_token(token: str, settings: Settings) -> str:
    """Decode a JWT and return the subject user ID."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
    if not isinstance(subject, str) or not subject:
        raise UnauthorizedError("Invalid token subject")
    return subject

