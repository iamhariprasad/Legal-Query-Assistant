"""Authentication and user schemas."""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for account registration."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=10, max_length=128)


class UserLogin(BaseModel):
    """Payload for login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    """Public user profile."""

    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

