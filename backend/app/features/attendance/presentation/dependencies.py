from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.attendance.application.services import AttendanceService
from app.features.attendance.application.use_cases import (
    BulkBusinessAttendanceUseCase,
    BulkEmployeeAttendanceUseCase,
    DeleteAttendanceUseCase,
    GetAttendanceUseCase,
    ListBusinessAttendanceUseCase,
    ListEmployeeAttendanceUseCase,
    UpsertAttendanceUseCase,
)
from app.features.attendance.infrastructure.repositories import SQLAttendanceRepository
from app.features.business.application.services import BusinessService
from app.features.business.infrastructure.repositories import SQLBusinessRepository
from app.features.employee.application.services import EmployeeService
from app.features.employee.infrastructure.repositories import SQLEmployeeRepository
from app.features.holiday.application.services import HolidayService
from app.features.holiday.infrastructure.repositories import SQLHolidaysRepository


def _services(db_session: AsyncSession):
    """Build the attendance + cross-feature services all bound to one session."""
    attendance_service = AttendanceService(SQLAttendanceRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    holiday_service = HolidayService(SQLHolidaysRepository(db_session))
    return attendance_service, employee_service, business_service, holiday_service


def get_upsert_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, employee_service, business_service, holiday_service = _services(db_session)
    return UpsertAttendanceUseCase(
        uow=SQLAlchemyUnitOfWork(db_session),
        attendance_service=attendance_service,
        business_service=business_service,
        employee_service=employee_service,
        holiday_service=holiday_service,
    )


def get_get_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, employee_service, business_service, _ = _services(db_session)
    return GetAttendanceUseCase(
        attendance_service=attendance_service,
        business_service=business_service,
        employee_service=employee_service,
    )


def get_list_employee_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, employee_service, business_service, _ = _services(db_session)
    return ListEmployeeAttendanceUseCase(
        attendance_service=attendance_service,
        business_service=business_service,
        employee_service=employee_service,
    )


def get_delete_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, employee_service, business_service, _ = _services(db_session)
    return DeleteAttendanceUseCase(
        uow=SQLAlchemyUnitOfWork(db_session),
        attendance_service=attendance_service,
        business_service=business_service,
        employee_service=employee_service,
    )


def get_bulk_employee_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, employee_service, business_service, _ = _services(db_session)
    return BulkEmployeeAttendanceUseCase(
        uow=SQLAlchemyUnitOfWork(db_session),
        attendance_service=attendance_service,
        business_service=business_service,
        employee_service=employee_service,
    )


def get_bulk_business_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, employee_service, business_service, holiday_service = _services(db_session)
    return BulkBusinessAttendanceUseCase(
        uow=SQLAlchemyUnitOfWork(db_session),
        attendance_service=attendance_service,
        business_service=business_service,
        employee_service=employee_service,
        holiday_service=holiday_service,
    )


def get_list_business_attendance_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    attendance_service, _, business_service, _ = _services(db_session)
    return ListBusinessAttendanceUseCase(
        attendance_service=attendance_service,
        business_service=business_service,
    )
