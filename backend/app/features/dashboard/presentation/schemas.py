"""Pydantic response schemas for the dashboard aggregate endpoint."""

from decimal import Decimal

from pydantic import BaseModel, field_serializer


def _serialize_decimal(value: Decimal) -> float:
    """Convert Decimal to float for JSON serialization."""
    return float(value)


class TrendDay(BaseModel):
    day: str
    date: str
    present: int
    half: int
    leave: int
    absent: int


class PayrollMonth(BaseModel):
    month: str
    label: str
    total: Decimal
    paid: Decimal

    @field_serializer("total", "paid")
    def serialize_decimals(self, value: Decimal) -> float:
        return _serialize_decimal(value)


class PayrollInfo(BaseModel):
    status: str
    total_payable: Decimal
    paid_count: int
    total_count: int

    @field_serializer("total_payable")
    def serialize_total_payable(self, value: Decimal) -> float:
        return _serialize_decimal(value)


class DashboardResponse(BaseModel):
    """Single aggregate payload for the owner dashboard."""

    business: dict[str, str]
    active_employees: int
    pending_attendance: int
    present_today: int
    half_today: int
    on_leave_today: int
    payroll: PayrollInfo
    monthly_additions: Decimal
    monthly_deductions: Decimal
    month: int
    month_name: str
    year: int
    trend: list[TrendDay]
    payroll_history: list[PayrollMonth]
    projected_monthly_cost: Decimal
    ytd_paid: Decimal

    @field_serializer(
        "monthly_additions",
        "monthly_deductions",
        "projected_monthly_cost",
        "ytd_paid",
    )
    def serialize_decimals(self, value: Decimal) -> float:
        return _serialize_decimal(value)
