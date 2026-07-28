from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.attendance.application.services import AttendanceService
from app.features.attendance.infrastructure.repositories import SQLAttendanceRepository
from app.features.business.application.services import BusinessService
from app.features.business.infrastructure.repositories import SQLBusinessRepository
from app.features.employee.application.services import EmployeeService
from app.features.employee.infrastructure.repositories import SQLEmployeeRepository
from app.features.holiday.application.services import HolidayService
from app.features.holiday.infrastructure.repositories import SQLHolidaysRepository
from app.features.payroll.application.services import PayrollService
from app.features.payroll.application.use_cases import (
    CreatePayrollRunUseCase,
    FinalizePayrollRunUseCase,
    GetPayrollRunUseCase,
    ListPayrollRunsUseCase,
)
from app.features.payroll.infrastructure.repositories import SQLPayrollRepository
from app.features.transaction.application.services import TransactionService
from app.features.transaction.infrastructure.repositories import SQLTransactionRepository


def _services(db_session: AsyncSession):
    """Build the payroll + 5 cross-feature services all bound to one session."""
    payroll_service = PayrollService(SQLPayrollRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    attendance_service = AttendanceService(SQLAttendanceRepository(db_session))
    holiday_service = HolidayService(SQLHolidaysRepository(db_session))
    transaction_service = TransactionService(SQLTransactionRepository(db_session))
    return (
        payroll_service,
        business_service,
        employee_service,
        attendance_service,
        holiday_service,
        transaction_service,
    )


def get_create_payroll_run_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    (
        payroll_service,
        business_service,
        employee_service,
        attendance_service,
        holiday_service,
        transaction_service,
    ) = _services(db_session)
    return CreatePayrollRunUseCase(
        uow=SQLAlchemyUnitOfWork(db_session),
        payroll_service=payroll_service,
        business_service=business_service,
        employee_service=employee_service,
        attendance_service=attendance_service,
        holiday_service=holiday_service,
        transaction_service=transaction_service,
    )


def get_get_payroll_run_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    payroll_service, business_service, *_ = _services(db_session)
    return GetPayrollRunUseCase(
        payroll_service=payroll_service,
        business_service=business_service,
    )


def get_list_payroll_runs_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    payroll_service, business_service, *_ = _services(db_session)
    return ListPayrollRunsUseCase(
        payroll_service=payroll_service,
        business_service=business_service,
    )


def get_finalize_payroll_run_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    payroll_service, business_service, *_ = _services(db_session)
    return FinalizePayrollRunUseCase(
        uow=SQLAlchemyUnitOfWork(db_session),
        payroll_service=payroll_service,
        business_service=business_service,
    )
