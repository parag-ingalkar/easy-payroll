"""Dashboard dependency wiring."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.features.attendance.application.services import AttendanceService
from app.features.attendance.infrastructure.repositories import SQLAttendanceRepository
from app.features.business.application.services import BusinessService
from app.features.business.infrastructure.repositories import SQLBusinessRepository
from app.features.dashboard.application.services import DashboardService
from app.features.employee.application.services import EmployeeService
from app.features.employee.infrastructure.repositories import SQLEmployeeRepository
from app.features.holiday.application.services import HolidayService
from app.features.holiday.infrastructure.repositories import SQLHolidaysRepository
from app.features.payroll.application.services import PayrollService
from app.features.payroll.infrastructure.repositories import SQLPayrollRepository
from app.features.transaction.application.services import TransactionService
from app.features.transaction.infrastructure.repositories import SQLTransactionRepository


def get_dashboard_service(
    db_session: AsyncSession = Depends(get_db),
) -> DashboardService:
    return DashboardService(
        business_service=BusinessService(SQLBusinessRepository(db_session)),
        employee_service=EmployeeService(SQLEmployeeRepository(db_session)),
        attendance_service=AttendanceService(SQLAttendanceRepository(db_session)),
        holiday_service=HolidayService(SQLHolidaysRepository(db_session)),
        payroll_service=PayrollService(SQLPayrollRepository(db_session)),
        transaction_service=TransactionService(SQLTransactionRepository(db_session)),
    )
