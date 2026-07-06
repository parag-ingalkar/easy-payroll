from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from app.core.config import get_settings


class UserRole(StrEnum):
    OWNER = "owner"
    EMPLOYEE = "employee"


@dataclass
class AccessToken:
    user_id: UUID
    roles: list[UserRole]
    created_at: datetime
    expires_at: datetime
    expires_in: int

    @staticmethod
    def create(user_id: UUID, roles: list[UserRole]):
        created_at = datetime.now(UTC)
        expires_in = get_settings().access_token_expire_minutes * 60
        expires_at = created_at + timedelta(seconds=expires_in)
        return AccessToken(
            user_id=user_id,
            roles=roles,
            created_at=created_at,
            expires_at=expires_at,
            expires_in=expires_in,
        )
