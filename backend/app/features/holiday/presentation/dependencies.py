from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.business.application.services import BusinessService
from app.features.business.infrastructure.repositories import SQLBusinessRepository
from app.features.holiday.application.services import HolidayService
from app.features.holiday.application.use_cases import (
    CreateHolidayUseCase,
    DeleteHolidayUseCase,
    GetHolidayUseCase,
    ListHolidaysUseCase,
)
from app.features.holiday.infrastructure.repositories import SQLHolidaysRepository


def get_create_holiday_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    holiday_service = HolidayService(SQLHolidaysRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return CreateHolidayUseCase(
        uow=uow, holiday_service=holiday_service, business_service=business_service
    )


def get_delete_holiday_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    holiday_service = HolidayService(SQLHolidaysRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return DeleteHolidayUseCase(
        uow=uow, holiday_service=holiday_service, business_service=business_service
    )


def get_list_holidays_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    holiday_service = HolidayService(SQLHolidaysRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return ListHolidaysUseCase(
        holiday_service=holiday_service, business_service=business_service
    )


def get_get_holiday_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    holiday_service = HolidayService(SQLHolidaysRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return GetHolidayUseCase(
        holiday_service=holiday_service, business_service=business_service
    )
