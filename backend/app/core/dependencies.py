from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_sessionmaker


async def get_db(
    session_factory: async_sessionmaker[AsyncSession] = Depends(get_sessionmaker),
):
    async with session_factory() as session:
        yield session
