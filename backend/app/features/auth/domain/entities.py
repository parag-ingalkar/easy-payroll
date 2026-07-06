from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.core.config import get_settings

from .value_objects import UserRole


@dataclass(slots=True, frozen=True)
class User:
    id: UUID
    email: str
    hashed_password: str
    name: str
    created_at: datetime
    updated_at: datetime
    roles: list[UserRole] = field(default_factory=lambda: [UserRole.OWNER])


@dataclass(slots=True, frozen=True)
class RefreshToken:
    id: UUID
    jti: str
    user_id: UUID
    expires_at: datetime
    created_at: datetime
    revoked: bool

    @staticmethod
    def create(user_id: UUID):
        now = datetime.now(UTC)
        return RefreshToken(
            id=uuid4(),
            jti=str(uuid4()),
            user_id=user_id,
            expires_at=now + timedelta(days=get_settings().refresh_token_expire_days),
            created_at=now,
            revoked=False,
        )

    def can_refresh(self) -> bool:
        return not self.revoked and datetime.now() < self.expires_at

    def revoke(self):
        return replace(self, revoked=True)

    def rotate(self) -> tuple["RefreshToken", "RefreshToken"]:
        new_token = RefreshToken.create(self.user_id)
        revoked_token = self.revoke()
        return new_token, revoked_token
