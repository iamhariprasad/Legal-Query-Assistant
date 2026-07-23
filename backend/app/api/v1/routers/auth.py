"""Authentication routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user, settings_dep
from app.core.config import Settings
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(settings_dep),
) -> User:
    """Register a user."""
    return await AuthService(session, settings).register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(settings_dep),
) -> TokenResponse:
    """Issue an access token."""
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        payload = UserLogin(
            email=str(form.get("username", "")),
            password=str(form.get("password", "")),
        )
    else:
        payload = UserLogin.model_validate(await request.json())
    return await AuthService(session, settings).login(payload)


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(current_user)) -> User:
    """Return authenticated user profile."""
    return user
