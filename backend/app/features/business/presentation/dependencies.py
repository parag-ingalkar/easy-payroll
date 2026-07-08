from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.auth.domain.entities import User
from app.features.auth.presentation.dependencies import get_current_user
from app.features.business.application.use_cases import (
    CreateBusinessUseCase,
    DeleteBusinessUseCase,
    UpdateBusinessUseCase,
)
from app.features.business.domain.entities import Business
from app.features.business.domain.exceptions import BusinessNotFoundError, BusinessNotOwnedError
from app.features.business.infrastructure.repositories import SQLBusinessRepository


def get_create_business_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return CreateBusinessUseCase(uow=uow, business_repo=business_repo)


def get_update_business_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return UpdateBusinessUseCase(uow=uow, business_repo=business_repo)


def get_delete_business_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return DeleteBusinessUseCase(uow=uow, business_repo=business_repo)


async def verify_business_ownership(
    business_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Business:
    """Dependency to verify that the current user owns the specified business."""
    business_repo = SQLBusinessRepository(session)
    business = await business_repo.get_by_id(business_id)
    if not business:
        raise BusinessNotFoundError
    if business.owner_id != current_user.id:
        raise BusinessNotOwnedError
    return business
