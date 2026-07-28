"""Pydantic request/response schemas for the payroll API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.payroll.domain.value_objects import PayrollStatus, PayrollWarningType


class CreatePayrollRunRequest(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=1900, le=9999)


class PayrollWarningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payroll_line_item_id: UUID
    warning_type: PayrollWarningType
    affected_dates: list[date]
    message: str
    created_at: datetime


class PayrollLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payroll_run_id: UUID
    business_id: UUID
    employee_id: UUID
    employee_name: str
    salary_type: str
    base_rate: Decimal
    divisor_policy_used: str | None
    overtime_multiplier_used: Decimal
    working_hours_used: Decimal
    present_days: Decimal
    half_days: Decimal
    paid_leave_days: Decimal
    unpaid_leave_days: Decimal
    holiday_days: int
    weekly_off_days_count: int
    overtime_hours: Decimal
    earned_salary: Decimal
    overtime_pay: Decimal
    total_additions: Decimal
    total_deductions: Decimal
    net_payable: Decimal
    status: PayrollStatus
    paid_via: str | None
    paid_date: date | None


class PayrollRunResponse(BaseModel):
    """A payroll run summary plus its nested line items and warnings."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    month: int
    year: int
    status: PayrollStatus
    total_amount_due: Decimal
    is_warning: bool
    created_at: datetime
    updated_at: datetime
    line_items: list[PayrollLineItemResponse] = Field(default_factory=list)
    warnings: list[PayrollWarningResponse] = Field(default_factory=list)
