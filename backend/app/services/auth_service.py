"""Authentication service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserCreate, UserLogin


class AuthService:
    """Register users and issue tokens."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.users = UserRepository(session)
        self.settings = settings

    async def register(self, payload: UserCreate) -> User:
        """Create a new user account."""
        existing = await self.users.get_by_email(str(payload.email))
        if existing:
            raise AppError("Email is already registered", code="email_exists", status_code=409)
        user = User(
            email=str(payload.email).lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        return await self.users.add(user)

    async def login(self, payload: UserLogin) -> TokenResponse:
        """Authenticate a user and return a JWT."""
        user = await self.users.get_by_email(str(payload.email))
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")
        return TokenResponse(access_token=create_access_token(user.id, self.settings))

