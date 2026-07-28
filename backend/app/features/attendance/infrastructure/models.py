"""SQLAlchemy ORM model for the attendance domain."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.domain.value_objects import AttendanceStatus

attendance_status_enum = SAEnum(
    AttendanceStatus,
    name="attendance_status_enum",
    values_callable=lambda x: [e.value for e in x],
)


class AttendanceModel(Base):
    """A single day's attendance for an employee.

    Uniqueness is enforced on ``(employee_id, date)`` via ``uq_attendance_employee_date``
    — one employee can have at most one attendance record per date.
    """

    __tablename__ = "attendances"
    __table_args__ = (UniqueConstraint("employee_id", "date", name="uq_attendance_employee_date"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(attendance_status_enum, nullable=False)
    overtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @classmethod
    def from_domain(cls, record: AttendanceRecord) -> "AttendanceModel":
        return cls(
            id=record.id,
            employee_id=record.employee_id,
            date=record.date,
            status=record.status,
            overtime_hours=record.overtime_hours,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def to_domain(self) -> AttendanceRecord:
        return AttendanceRecord(
            id=self.id,
            employee_id=self.employee_id,
            date=self.date,
            status=self.status,
            overtime_hours=self.overtime_hours,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
