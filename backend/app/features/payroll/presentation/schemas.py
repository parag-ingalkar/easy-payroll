"""Pydantic request/response schemas for the payroll API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.features.payroll.domain.value_objects import (
    PaymentMethod,
    PayrollStatus,
    PayrollWarningType,
)


def _serialize_decimal(value: Decimal) -> float:
    """Convert Decimal to float for JSON serialization."""
    return float(value)


class CreatePayrollRunRequest(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=1900, le=9999)


class MarkPaidRequest(BaseModel):
    paid_via: PaymentMethod
    paid_date: date | None = None


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

    @field_serializer(
        "base_rate",
        "overtime_multiplier_used",
        "working_hours_used",
        "present_days",
        "half_days",
        "paid_leave_days",
        "unpaid_leave_days",
        "overtime_hours",
        "earned_salary",
        "overtime_pay",
        "total_additions",
        "total_deductions",
        "net_payable",
    )
    def serialize_decimals(self, value: Decimal) -> float:
        return _serialize_decimal(value)


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
    is_paid: bool = Field(default=False, description="True if all line items are paid")

    @field_serializer("total_amount_due")
    def serialize_total_amount_due(self, value: Decimal) -> float:
        return _serialize_decimal(value)
