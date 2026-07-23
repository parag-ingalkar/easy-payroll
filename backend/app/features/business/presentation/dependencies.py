from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.auth.domain.entities import CurrentUser
from app.features.auth.presentation.dependencies import get_current_user
from app.features.business.application.services import BusinessService
from app.features.business.application.use_cases import (
    CreateBusinessUseCase,
    DeleteBusinessUseCase,
    ListBusinessesUseCase,
    UpdateBusinessUseCase,
)
from app.features.business.domain.entities import Business
from app.features.business.domain.exceptions import BusinessNotFoundError, BusinessNotOwnedError
from app.features.business.infrastructure.repositories import SQLBusinessRepository


def get_create_business_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return CreateBusinessUseCase(uow=uow, business_service=business_service)


def get_update_business_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return UpdateBusinessUseCase(uow=uow, business_service=business_service)


def get_delete_business_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return DeleteBusinessUseCase(uow=uow, business_service=business_service)

def get_list_businesses_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return ListBusinessesUseCase(business_service=business_service)


async def verify_business_ownership(
    business_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Business:
    """Dependency to verify that the current user owns the specified business."""
    business_service = BusinessService(SQLBusinessRepository(session))
    business = await business_service.get_by_id(business_id)
    if not business:
        raise BusinessNotFoundError
    if business.owner_id != current_user.id:
        raise BusinessNotOwnedError
    return business
