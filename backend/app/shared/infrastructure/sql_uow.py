from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.features.auth.infrastructure.repositories import SQLTokenRepository, SQLUserRepository
from app.shared.application.uow_port import UnitOfWorkPort


class SQLUnitOfWork(UnitOfWorkPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLUnitOfWork":
        self.session = self._session_factory()
        self.user_repo = SQLUserRepository(self.session)
        self.refresh_token_repo = SQLTokenRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            if self.session is not None:
                await self.session.close()

    async def commit(self) -> None:
        if self.session is not None:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()
