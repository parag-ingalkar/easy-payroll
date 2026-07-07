from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_sessionmaker
from app.shared.application.uow_port import UnitOfWorkPort
from app.shared.infrastructure.sql_uow import SQLUnitOfWork


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return get_sessionmaker()


async def get_db(
    session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory),
):
    async with session_factory() as session:
        yield session


def get_uow(
    session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory),
) -> UnitOfWorkPort:
    return SQLUnitOfWork(session_factory)
