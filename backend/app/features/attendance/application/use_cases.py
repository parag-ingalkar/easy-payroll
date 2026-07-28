from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.core.uow import AbstractUnitOfWork
from app.features.attendance.application.commands import (
    BulkBusinessAttendanceCommand,
    BulkEmployeeAttendanceCommand,
    DeleteAttendanceCommand,
    GetAttendanceCommand,
    ListBusinessAttendanceCommand,
    ListEmployeeAttendanceCommand,
    UpsertAttendanceCommand,
)
from app.features.attendance.application.ports import (
    BusinessServicePort,
    EmployeeServicePort,
    HolidayServicePort,
)
from app.features.attendance.application.services import AttendanceService
from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.domain.exceptions import CannotMarkAttendance
from app.features.attendance.domain.value_objects import AttendanceStatus
from app.features.employee.domain.entities import Employee


@dataclass
class UpsertAttendanceUseCase:
    """Full-replace upsert of a single day's attendance (PUT by date)."""

    uow: AbstractUnitOfWork
    attendance_service: AttendanceService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort
    holiday_service: HolidayServicePort

    async def execute(self, command: UpsertAttendanceCommand) -> AttendanceRecord:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            employee = await self.employee_service.get_owned_employee(
                command.employee_id, business.id
            )

            existing = await self.attendance_service.get_by_employee_and_date(
                employee.id, command.attendance_date
            )
            if employee.is_date_weekly_off(command.attendance_date):
                raise CannotMarkAttendance(attendance_date=command.attendance_date)

            holiday = await self.holiday_service.get_by_business_and_date(
                business.id, command.attendance_date
            )
            if holiday is not None:
                raise CannotMarkAttendance(attendance_date=command.attendance_date)

            if existing is not None:
                existing.update(
                    status=command.status,
                    overtime_hours=command.overtime_hours,
                )
                record = existing
            else:
                record = AttendanceRecord.create(
                    employee_id=employee.id,
                    date=command.attendance_date,
                    status=command.status,
                    overtime_hours=command.overtime_hours,
                )
            await self.attendance_service.upsert(record)
            return record


@dataclass
class GetAttendanceUseCase:
    attendance_service: AttendanceService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: GetAttendanceCommand) -> AttendanceRecord:
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )
        employee = await self.employee_service.get_owned_employee(command.employee_id, business.id)
        return await self.attendance_service.get_or_raise(employee.id, command.attendance_date)


@dataclass
class ListEmployeeAttendanceUseCase:
    attendance_service: AttendanceService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: ListEmployeeAttendanceCommand) -> list[AttendanceRecord]:
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )
        employee = await self.employee_service.get_owned_employee(command.employee_id, business.id)

        # Default to an unbounded range when no year/month filter is given.
        start, end = _month_bounds_or_unbounded(command.year, command.month)
        records = await self.attendance_service.list_by_employee_and_date_range(
            employee.id, start, end
        )
        return list(records)


@dataclass
class DeleteAttendanceUseCase:
    uow: AbstractUnitOfWork
    attendance_service: AttendanceService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: DeleteAttendanceCommand) -> None:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            employee = await self.employee_service.get_owned_employee(
                command.employee_id, business.id
            )
            record = await self.attendance_service.get_or_raise(
                employee.id, command.attendance_date
            )
            await self.attendance_service.delete(record)


@dataclass
class BulkEmployeeAttendanceUseCase:
    """Mark attendance for one employee across multiple days."""

    uow: AbstractUnitOfWork
    attendance_service: AttendanceService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: BulkEmployeeAttendanceCommand) -> list[AttendanceRecord]:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            employee = await self.employee_service.get_owned_employee(
                command.employee_id, business.id
            )

            records: list[AttendanceRecord] = []
            for entry in command.entries:
                existing = await self.attendance_service.get_by_employee_and_date(
                    employee.id, entry.date
                )
                records.append(
                    _resolve_record(
                        employee,
                        entry.date,
                        entry.status,
                        entry.overtime_hours,
                        existing,
                    )
                )
            await self.attendance_service.bulk_upsert(records)
            return records


@dataclass
class BulkBusinessAttendanceUseCase:
    """Mark attendance for multiple employees on a single date."""

    uow: AbstractUnitOfWork
    attendance_service: AttendanceService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort
    holiday_service: HolidayServicePort

    async def execute(self, command: BulkBusinessAttendanceCommand) -> list[AttendanceRecord]:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )

            holiday = await self.holiday_service.get_by_business_and_date(
                business.id, command.attendance_date
            )
            if holiday is not None:
                raise CannotMarkAttendance(attendance_date=command.attendance_date)

            records: list[AttendanceRecord] = []
            for entry in command.entries:
                # Validate every referenced employee belongs to this business.
                employee = await self.employee_service.get_owned_employee(
                    entry.employee_id, business.id
                )
                if employee.is_date_weekly_off(command.attendance_date):
                    raise CannotMarkAttendance(attendance_date=command.attendance_date)

                existing = await self.attendance_service.get_by_employee_and_date(
                    employee.id, command.attendance_date
                )
                records.append(
                    _resolve_record(
                        employee,
                        command.attendance_date,
                        entry.status,
                        entry.overtime_hours,
                        existing,
                    )
                )
            await self.attendance_service.bulk_upsert(records)
            return records


@dataclass
class ListBusinessAttendanceUseCase:
    attendance_service: AttendanceService
    business_service: BusinessServicePort

    async def execute(self, command: ListBusinessAttendanceCommand) -> list[AttendanceRecord]:
        await self.business_service.get_owned_business(command.business_id, command.current_user.id)
        records = await self.attendance_service.list_by_business_and_date(
            command.business_id, command.attendance_date
        )
        return list(records)


# --- helpers ---------------------------------------------------------------


def _month_bounds_or_unbounded(year: int | None, month: int | None) -> tuple[date, date]:
    """Return the (start, end) date range for a year/month, or an unbounded range."""
    if year is not None and month is not None:
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        return date(year, month, 1), date(year, month, last_day)
    return date.min, date.max


def _resolve_record(
    employee: Employee,
    attendance_date: date,
    status: AttendanceStatus,
    overtime_hours: Decimal,
    existing: AttendanceRecord | None,
) -> AttendanceRecord:
    """Return an existing record updated in place, or a brand-new record."""
    if existing is not None:
        existing.update(status=status, overtime_hours=overtime_hours)
        return existing
    if employee.is_date_weekly_off(attendance_date):
        raise CannotMarkAttendance(attendance_date=attendance_date)
    return AttendanceRecord.create(
        employee_id=employee.id,
        date=attendance_date,
        status=status,
        overtime_hours=overtime_hours,
    )
