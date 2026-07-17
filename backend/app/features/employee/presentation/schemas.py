"""Pydantic request/response schemas for the employee API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.employee.domain.value_objects import SalaryType
from app.shared.enums import WeekDay


class CreateEmployeeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=15)
    designation: str | None = Field(default=None, max_length=100)
    salary_type: SalaryType
    base_rate: Decimal = Field(..., max_digits=10, decimal_places=2)
    joining_date: date | None = None
    overtime_multiplier: Decimal | None = Field(default=None, max_digits=3, decimal_places=1)
    weekly_off_days: list[WeekDay] | None = None
    working_hours: Decimal | None = Field(default=None, ge=1, le=24)


class UpdateEmployeeRequest(BaseModel):
    """Every field optional — PATCH semantics. Only provided fields are applied."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=15)
    designation: str | None = Field(default=None, max_length=100)
    salary_type: SalaryType | None = None
    base_rate: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    overtime_multiplier: Decimal | None = Field(default=None, max_digits=3, decimal_places=1)
    weekly_off_days: list[WeekDay] | None = None
    working_hours: Decimal | None = Field(default=None, ge=1, le=24)
    joining_date: date | None = None


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    name: str
    phone: str | None
    designation: str | None
    salary_type: SalaryType
    base_rate: Decimal
    overtime_multiplier: Decimal
    weekly_off_days: list[WeekDay]
    working_hours: int
    joining_date: date | None
    is_active: bool
    created_at: datetime
