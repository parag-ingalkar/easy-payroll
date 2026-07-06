from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.application.ports import TokenRepositoryPort, UserRepositoryPort
from app.features.auth.domain.entities import RefreshToken, User
from app.features.auth.infrastructure.models import RefreshTokenModel, UserModel


class SQLUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_id(self, id: UUID) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def add(self, user: User) -> None:
        user_model = UserModel.from_domain(user)
        self.session.add(user_model)


class SQLTokenRepository(TokenRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        """Fetches a refresh token by its JTI."""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.jti == jti)
        )
        token_model = result.scalar_one_or_none()
        return token_model.to_domain() if token_model else None

    async def add(self, refresh_token: RefreshToken) -> None:
        """Adds a new refresh token to the repository."""
        refresh_token_model = RefreshTokenModel.from_domain(refresh_token)
        self.session.add(refresh_token_model)

    async def revoke(self, refresh_token: RefreshToken) -> None:
        """Marks a refresh token as revoked."""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.jti == refresh_token.jti)
            .values(revoked=True)
        )
