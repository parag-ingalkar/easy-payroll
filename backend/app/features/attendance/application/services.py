from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.features.attendance.application.ports import AttendanceRepositoryPort
from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.domain.exceptions import AttendanceNotFoundError


@dataclass
class AttendanceService:
    """Application service — the sole gateway to ``AttendanceRepositoryPort``.

    Own-feature use cases depend on this concrete class. Cross-feature
    consumers (e.g. payroll) declare their own narrow ``Protocol`` port
    (``AttendanceServicePort``) which this class satisfies structurally.
    """

    attendance_repo: AttendanceRepositoryPort

    async def get_or_raise(self, employee_id: UUID, attendance_date: date) -> AttendanceRecord:
        """Fetch a record by (employee, date), raising if absent."""
        record = await self.attendance_repo.get_by_employee_and_date(employee_id, attendance_date)
        if not record:
            raise AttendanceNotFoundError(employee_id=employee_id, attendance_date=attendance_date)
        return record

    async def get_by_employee_and_date(
        self, employee_id: UUID, attendance_date: date
    ) -> AttendanceRecord | None:
        return await self.attendance_repo.get_by_employee_and_date(employee_id, attendance_date)

    async def upsert(self, record: AttendanceRecord) -> None:
        await self.attendance_repo.upsert(record)

    async def bulk_upsert(self, records: Sequence[AttendanceRecord]) -> None:
        await self.attendance_repo.bulk_upsert(records)

    async def list_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> Sequence[AttendanceRecord]:
        return await self.attendance_repo.list_by_employee_and_date_range(
            employee_id, start_date, end_date
        )

    async def list_by_business_and_date(
        self, business_id: UUID, attendance_date: date
    ) -> Sequence[AttendanceRecord]:
        return await self.attendance_repo.list_by_business_and_date(business_id, attendance_date)

    async def delete(self, record: AttendanceRecord) -> None:
        await self.attendance_repo.delete(record)
