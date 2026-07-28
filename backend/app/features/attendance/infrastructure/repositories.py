"""SQLAlchemy repository for the attendance domain.

Upsert semantics deviate from the simple ``add``/``flush`` pattern used by
other features: attendance records are PUT/full-replace resources keyed by
``(employee_id, date)``, so inserts and updates must be resolved server-side
against the unique constraint. We use PostgreSQL's ``ON CONFLICT ... DO
UPDATE`` (``sqlalchemy.dialects.postgresql.insert``) for both single and bulk
upserts. This keeps a bulk "mark all present" call to a single round-trip.
"""

from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.attendance.application.ports import AttendanceRepositoryPort
from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.infrastructure.models import AttendanceModel


class SQLAttendanceRepository(AttendanceRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_employee_and_date(
        self, employee_id: UUID, attendance_date: date
    ) -> AttendanceRecord | None:
        """Retrieve an attendance record by employee ID and date."""
        result = await self.session.execute(
            select(AttendanceModel).where(
                AttendanceModel.employee_id == employee_id,
                AttendanceModel.date == attendance_date,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def upsert(self, record: AttendanceRecord) -> None:
        """Insert or full-replace a single attendance record (one statement)."""
        await self.session.execute(
            pg_insert(AttendanceModel)
            .values(
                id=record.id,
                employee_id=record.employee_id,
                date=record.date,
                status=record.status,
                overtime_hours=record.overtime_hours,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            .on_conflict_do_update(
                index_elements=[AttendanceModel.employee_id, AttendanceModel.date],
                set_={
                    "status": record.status,
                    "overtime_hours": record.overtime_hours,
                    "updated_at": record.updated_at,
                },
            )
        )
        await self.session.flush()

    async def bulk_upsert(self, records: Sequence[AttendanceRecord]) -> None:
        """Insert or full-replace many records in a single statement."""
        if not records:
            return
        await self.session.execute(
            pg_insert(AttendanceModel)
            .values(
                [
                    {
                        "id": r.id,
                        "employee_id": r.employee_id,
                        "date": r.date,
                        "status": r.status,
                        "overtime_hours": r.overtime_hours,
                        "created_at": r.created_at,
                        "updated_at": r.updated_at,
                    }
                    for r in records
                ]
            )
            .on_conflict_do_update(
                index_elements=[AttendanceModel.employee_id, AttendanceModel.date],
                set_={
                    "status": AttendanceModel.status,
                    "overtime_hours": AttendanceModel.overtime_hours,
                    "updated_at": AttendanceModel.updated_at,
                },
            )
        )
        await self.session.flush()

    async def list_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> Sequence[AttendanceRecord]:
        """List records for an employee within a date range (inclusive)."""
        result = await self.session.execute(
            select(AttendanceModel)
            .where(
                AttendanceModel.employee_id == employee_id,
                AttendanceModel.date >= start_date,
                AttendanceModel.date <= end_date,
            )
            .order_by(AttendanceModel.date.asc())
        )
        return [m.to_domain() for m in result.scalars().all()]

    async def list_by_business_and_date(
        self, business_id: UUID, attendance_date: date
    ) -> Sequence[AttendanceRecord]:
        """List records for every employee of a business on a given date.

        Joins through ``employees`` to scope by ``business_id``.
        """
        from app.features.employee.infrastructure.models import EmployeeModel

        result = await self.session.execute(
            select(AttendanceModel)
            .join(EmployeeModel, EmployeeModel.id == AttendanceModel.employee_id)
            .where(
                EmployeeModel.business_id == business_id,
                AttendanceModel.date == attendance_date,
            )
            .order_by(EmployeeModel.name.asc())
        )
        return [m.to_domain() for m in result.scalars().all()]

    async def delete(self, record: AttendanceRecord) -> None:
        """Delete an attendance record."""
        model = await self.session.get(AttendanceModel, record.id)
        if model is None:
            return
        await self.session.delete(model)
        await self.session.flush()
