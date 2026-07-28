"""Attendance-domain entities — pure Python dataclasses."""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.features.attendance.domain.exceptions import (
    AttendanceNotOwnedError,
    InvalidOvertimeHoursError,
)
from app.features.attendance.domain.value_objects import AttendanceStatus


@dataclass
class AttendanceRecord:
    """A single day's attendance for an employee.

    An attendance record is identified by the composite key
    ``(employee_id, date)`` — one employee can have at most one attendance per
    date. The endpoint contract therefore uses a PUT/full-replace upsert keyed
    by date (no separate attendance id is exposed in the URL).

    ``overtime_hours`` is always >= 0 (the ``>= 0`` invariant is owned by this
    entity and enforced in :meth:`create` and :meth:`update`).
    """

    id: UUID
    employee_id: UUID
    date: date
    status: AttendanceStatus
    overtime_hours: Decimal
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def _validate_overtime(overtime_hours: Decimal) -> None:
        if overtime_hours < 0:
            raise InvalidOvertimeHoursError(overtime_hours=overtime_hours)

    @classmethod
    def create(
        cls,
        *,
        employee_id: UUID,
        date: date,
        status: AttendanceStatus,
        overtime_hours: Decimal,
    ) -> "AttendanceRecord":
        """Factory method for creating a new attendance record entity."""
        cls._validate_overtime(overtime_hours)
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            employee_id=employee_id,
            date=date,
            status=status,
            overtime_hours=overtime_hours,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        status: AttendanceStatus | None = None,
        overtime_hours: Decimal | None = None,
    ) -> None:
        """Update the attendance record (PATCH semantics). Only provided fields are applied.

        ``date`` and ``employee_id`` are never changed here — they form the
        composite key of the record.
        """
        if status is not None:
            self.status = status
        if overtime_hours is not None:
            self._validate_overtime(overtime_hours)
            self.overtime_hours = overtime_hours
        self.updated_at = datetime.now(UTC)

    def ensure_belongs_to_employee(self, employee_id: UUID) -> None:
        """Ensure that this record belongs to the given employee."""
        if self.employee_id != employee_id:
            raise AttendanceNotOwnedError(attendance_id=self.id, employee_id=employee_id)
