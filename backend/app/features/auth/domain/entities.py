from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.features.auth.domain.value_objects import UserRole
from app.shared.utils import get_now


@dataclass(slots=True, frozen=True)
class User:
    id: UUID
    email: str
    hashed_password: str
    name: str
    created_at: datetime
    updated_at: datetime
    roles: list[UserRole] = field(default_factory=lambda: [UserRole.OWNER])

    @staticmethod
    def create(
        email: str, hashed_password: str, name: str, roles: list[UserRole] | None = None
    ) -> "User":
        now = get_now()
        return User(
            id=uuid4(),
            email=email.lower(),
            hashed_password=hashed_password,
            name=name,
            created_at=now,
            updated_at=now,
            roles=roles if roles is not None else [UserRole.OWNER],
        )


@dataclass(slots=True)
class RefreshToken:
    id: UUID
    jti: str
    user_id: UUID
    expires_at: datetime
    created_at: datetime
    revoked: bool

    @staticmethod
    def create(user_id: UUID):
        now = get_now()
        return RefreshToken(
            id=uuid4(),
            jti=str(uuid4()),
            user_id=user_id,
            expires_at=now + timedelta(days=get_settings().refresh_token_expire_days),
            created_at=now,
            revoked=False,
        )

    def can_refresh(self) -> bool:
        return not self.revoked and get_now() < self.expires_at

    def revoke(self):
        self.revoked = True
