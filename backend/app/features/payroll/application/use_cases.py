"""Payroll use cases — orchestration of the payroll engine over persisted data.

The ``CreatePayrollRunUseCase`` is the "run payroll" entry point: it loads
employees/holidays/attendance/transactions for the period, feeds them through
the pure-Python engine (:mod:`app.features.payroll.domain.services`), and
persists the run with all line items and warnings in a single transaction.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.core.uow import AbstractUnitOfWork
from app.features.payroll.application.commands import (
    CreatePayrollRunCommand,
    FinalizePayrollRunCommand,
    GetPayrollRunCommand,
    ListPayrollRunsCommand,
)
from app.features.payroll.application.ports import (
    AttendanceServicePort,
    BusinessServicePort,
    EmployeeServicePort,
    HolidayServicePort,
    TransactionServicePort,
)
from app.features.payroll.application.services import PayrollService
from app.features.payroll.domain.entities import (
    PayrollLineItem,
    PayrollRun,
    PayrollWarning,
)
from app.features.payroll.domain.exceptions import PayrollRunAlreadyExistsError
from app.features.payroll.domain.services import (
    calculate_line_item_values,
    generate_warnings_for_line_item,
    sum_transactions,
    summarize_attendance,
)


@dataclass
class PayrollRunResult:
    """A payroll run plus its computed line items and warnings."""

    run: PayrollRun
    line_items: Sequence[PayrollLineItem]
    warnings: Sequence[PayrollWarning]


@dataclass
class CreatePayrollRunUseCase:
    """Compute and persist a payroll run for a business for a (year, month)."""

    uow: AbstractUnitOfWork
    payroll_service: PayrollService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort
    attendance_service: AttendanceServicePort
    holiday_service: HolidayServicePort
    transaction_service: TransactionServicePort

    async def execute(self, command: CreatePayrollRunCommand) -> PayrollRunResult:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )

            # One business → at most one run per (year, month).
            existing = await self.payroll_service.get_by_business_and_period(
                business.id, command.year, command.month
            )
            if existing is not None:
                raise PayrollRunAlreadyExistsError(
                    business_id=business.id, year=command.year, month=command.month
                )

            start_date, end_date = _month_bounds(command.year, command.month)

            holidays = await self.holiday_service.list_by_business(
                business.id, command.year, command.month
            )
            paid_holiday_dates = {h.holiday_date for h in holidays if h.is_paid}

            employees = await self.employee_service.list_by_business(business.id)

            run = PayrollRun.create(business_id=business.id, month=command.month, year=command.year)

            line_items: list[PayrollLineItem] = []
            warnings: list[PayrollWarning] = []
            total_amount_due = Decimal("0")
            is_warning = False

            for employee in employees:
                attendance = await self.attendance_service.list_by_employee_and_date_range(
                    employee.id, start_date, end_date
                )
                transactions = await self.transaction_service.get_by_employee_and_date_range(
                    employee.id, start_date, end_date
                )

                summary = summarize_attendance(
                    list(attendance),
                    list(employee.weekly_off_days),
                    paid_holiday_dates,
                    command.year,
                    command.month,
                )
                totals = sum_transactions(transactions)

                line_item = calculate_line_item_values(
                    run_id=run.id,
                    business_id=business.id,
                    employee_id=employee.id,
                    employee_name=employee.name,
                    salary_type=employee.salary_type.value,
                    base_rate=employee.base_rate,
                    divisor_policy=business.divisor_policy.value,
                    overtime_multiplier=employee.overtime_multiplier,
                    working_hours=employee.working_hours,
                    attendance=summary,
                    transaction_totals=totals,
                    year=command.year,
                    month=command.month,
                )
                line_items.append(line_item)
                total_amount_due += line_item.net_payable

                item_warnings = generate_warnings_for_line_item(
                    line_item_id=line_item.id,
                    weekly_off_days=list(employee.weekly_off_days),
                    records=list(attendance),
                    paid_holiday_dates=paid_holiday_dates,
                    year=command.year,
                    month=command.month,
                )
                if item_warnings:
                    is_warning = True
                    warnings.extend(item_warnings)

            run.set_summary(total_amount_due=total_amount_due, is_warning=is_warning)

            await self.payroll_service.add_run(run)
            if line_items:
                await self.payroll_service.add_line_items(line_items)
            if warnings:
                await self.payroll_service.add_warnings(warnings)

            return PayrollRunResult(run=run, line_items=line_items, warnings=warnings)


@dataclass
class GetPayrollRunUseCase:
    payroll_service: PayrollService
    business_service: BusinessServicePort

    async def execute(self, command: GetPayrollRunCommand) -> PayrollRunResult:
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )
        run = await self.payroll_service.get_run_by_id_or_raise(command.payroll_id)
        run.ensure_owned_by_business(business.id)
        line_items = await self.payroll_service.list_line_items(run.id)
        warnings = await self.payroll_service.list_warnings(run.id)
        return PayrollRunResult(run=run, line_items=line_items, warnings=warnings)


@dataclass
class ListPayrollRunsUseCase:
    payroll_service: PayrollService
    business_service: BusinessServicePort

    async def execute(self, command: ListPayrollRunsCommand) -> Sequence[PayrollRun]:
        await self.business_service.get_owned_business(command.business_id, command.current_user.id)
        return await self.payroll_service.list_by_business(command.business_id)


@dataclass
class FinalizePayrollRunUseCase:
    uow: AbstractUnitOfWork
    payroll_service: PayrollService
    business_service: BusinessServicePort

    async def execute(self, command: FinalizePayrollRunCommand) -> PayrollRun:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            run = await self.payroll_service.get_run_by_id_or_raise(command.payroll_id)
            run.ensure_owned_by_business(business.id)
            run.finalize()
            await self.payroll_service.update_run(run)
            return run


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    """Return the inclusive (first, last) date of the given year/month."""
    from calendar import monthrange

    _, last_day = monthrange(year, month)
    return date(year, month, 1), date(year, month, last_day)
