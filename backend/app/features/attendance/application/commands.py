from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.features.attendance.domain.value_objects import AttendanceStatus
from app.features.auth.domain.entities import CurrentUser


@dataclass(frozen=True)
class UpsertAttendanceCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    attendance_date: date
    status: AttendanceStatus
    overtime_hours: Decimal


@dataclass(frozen=True)
class GetAttendanceCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    attendance_date: date


@dataclass(frozen=True)
class ListEmployeeAttendanceCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    year: int | None = None
    month: int | None = None


@dataclass(frozen=True)
class DeleteAttendanceCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    attendance_date: date


@dataclass(frozen=True)
class BulkEmployeeAttendanceEntry:
    """One day's attendance for the bulk-by-employee payload (one employee, many days)."""

    date: date
    status: AttendanceStatus
    overtime_hours: Decimal = Decimal("0")


@dataclass(frozen=True)
class BulkEmployeeAttendanceCommand:
    """Mark attendance for a single employee across multiple days."""

    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    entries: Sequence[BulkEmployeeAttendanceEntry]


@dataclass(frozen=True)
class BulkBusinessAttendanceEntry:
    """One employee's attendance for the bulk-by-business payload (one date, many employees)."""

    employee_id: UUID
    status: AttendanceStatus
    overtime_hours: Decimal = Decimal("0")


@dataclass(frozen=True)
class BulkBusinessAttendanceCommand:
    """Mark attendance for multiple employees on a single date (e.g. "mark all present")."""

    current_user: CurrentUser
    business_id: UUID
    attendance_date: date
    entries: Sequence[BulkBusinessAttendanceEntry]


@dataclass(frozen=True)
class ListBusinessAttendanceCommand:
    """Load the current attendance state for every employee of a business on one date."""

    current_user: CurrentUser
    business_id: UUID
    attendance_date: date
