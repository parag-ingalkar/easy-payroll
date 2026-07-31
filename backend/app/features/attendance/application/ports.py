from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import UUID

from app.features.attendance.domain.entities import AttendanceRecord
from app.features.business.domain.entities import Business
from app.features.employee.domain.entities import Employee
from app.features.holiday.domain.entities import Holiday


class AttendanceRepositoryPort(Protocol):
    """Protocol for the attendance repository."""

    async def get_by_employee_and_date(
        self, employee_id: UUID, attendance_date: date
    ) -> AttendanceRecord | None:
        """Retrieve an attendance record by employee ID and date."""
        ...

    async def upsert(self, record: AttendanceRecord) -> None:
        """Insert or update (full-replace) a single attendance record."""
        ...

    async def bulk_upsert(self, records: Sequence[AttendanceRecord]) -> None:
        """Insert or update (full-replace) many attendance records in one statement."""
        ...

    async def list_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> Sequence[AttendanceRecord]:
        """List attendance records for an employee within a date range (inclusive)."""
        ...

    async def list_by_business_and_date(
        self, business_id: UUID, attendance_date: date
    ) -> Sequence[AttendanceRecord]:
        """List attendance records for every employee of a business on a given date."""
        ...

    async def delete(self, record: AttendanceRecord) -> None:
        """Delete an attendance record."""
        ...


class BusinessServicePort(Protocol):
    """Cross-feature port for the attendance feature to access business capability.

    Satisfied structurally by ``BusinessService`` (business feature). Defined
    here — the consumer — per hexagonal/ports-and-adapters convention.
    """

    async def get_owned_business(self, business_id: UUID, owner_id: UUID) -> Business:
        """Fetch a business and verify it is owned by ``owner_id``."""
        ...


class EmployeeServicePort(Protocol):
    """Cross-feature port for the attendance feature to access employee capability.

    Satisfied structurally by ``EmployeeService`` (employee feature). Defined
    here — the consumer — per hexagonal/ports-and-adapters convention.
    """

    async def get_owned_employee(self, employee_id: UUID, business_id: UUID) -> Employee:
        """Fetch an employee and verify it belongs to the given business."""
        ...

    async def list_by_business(
        self, business_id: UUID, include_inactive: bool = False
    ) -> list[Employee]:
        """List employees belonging to a business."""
        ...


class HolidayServicePort(Protocol):
    """Cross-feature port for the attendance feature to access holiday capability.

    Satisfied structurally by ``HolidayService`` (holiday feature). Defined
    here — the consumer — per hexagonal/ports-and-adapters convention.
    """

    async def get_by_business_and_date(
        self, business_id: UUID, holiday_date: date
    ) -> Holiday | None:
        """Fetch a holiday by business ID and date."""
        ...
