from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.features.auth.domain.entities import RefreshToken, User
from app.features.auth.domain.value_objects import UserRole

user_role_type = SAEnum(
    UserRole,
    name="user_role_enum",
    values_callable=lambda x: [e.value for e in x],
)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    roles: Mapped[list[UserRole]] = mapped_column(
        ARRAY(user_role_type),
        nullable=False,
        default=[UserRole.OWNER],
    )

    refresh_tokens = relationship(
        "RefreshTokenModel", back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[role.value for role in user.roles],
        )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            name=self.name,
            created_at=self.created_at,
            updated_at=self.updated_at,
            roles=[UserRole(role) for role in self.roles],
        )


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user = relationship("UserModel", back_populates="refresh_tokens")

    @classmethod
    def from_domain(cls, refresh_token: "RefreshToken") -> "RefreshTokenModel":
        return cls(
            id=refresh_token.id,
            jti=refresh_token.jti,
            user_id=refresh_token.user_id,
            expires_at=refresh_token.expires_at,
            created_at=refresh_token.created_at,
            revoked=refresh_token.revoked,
        )

    def to_domain(self) -> "RefreshToken":
        return RefreshToken(
            id=self.id,
            jti=self.jti,
            user_id=self.user_id,
            expires_at=self.expires_at,
            created_at=self.created_at,
            revoked=self.revoked,
        )
