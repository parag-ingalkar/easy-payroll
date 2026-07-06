from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.features.auth.domain.value_objects import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=120)
    name: str = Field(min_length=1, max_length=120)


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=120)
    password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    roles: list[UserRole]

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int

    model_config = ConfigDict(from_attributes=True)
