"""Pydantic request/response schemas for the attendance API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.features.attendance.domain.value_objects import AttendanceStatus


def _serialize_decimal(value: Decimal) -> float:
    """Convert Decimal to float for JSON serialization."""
    return float(value)


class UpsertAttendanceRequest(BaseModel):
    """Full body for a PUT upsert by date (status + overtime replace the record)."""

    status: AttendanceStatus
    overtime_hours: Decimal = Field(default=Decimal("0"), ge=0, max_digits=6, decimal_places=2)


class BulkEmployeeAttendanceEntry(BaseModel):
    """One day's attendance for the one-employee-many-days bulk payload."""

    date: date
    status: AttendanceStatus
    overtime_hours: Decimal = Field(default=Decimal("0"), ge=0, max_digits=6, decimal_places=2)


class BulkBusinessAttendanceEntry(BaseModel):
    """One employee's attendance for the one-date-many-employees bulk payload."""

    employee_id: UUID
    status: AttendanceStatus
    overtime_hours: Decimal = Field(default=Decimal("0"), ge=0, max_digits=6, decimal_places=2)


class BulkEmployeeAttendanceRequest(BaseModel):
    """Mark attendance for a single employee across multiple days."""

    entries: list[BulkEmployeeAttendanceEntry] = Field(..., min_length=1)


class BulkBusinessAttendanceRequest(BaseModel):
    """Mark attendance for multiple employees on a single date (e.g. "mark all present")."""

    entries: list[BulkBusinessAttendanceEntry] = Field(..., min_length=1)


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    date: date
    status: AttendanceStatus
    overtime_hours: Decimal
    created_at: datetime
    updated_at: datetime

    @field_serializer("overtime_hours")
    def serialize_overtime_hours(self, value: Decimal) -> float:
        return _serialize_decimal(value)
