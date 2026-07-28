"""Payroll domain services — pure-Python salary calculation + warning generation.

These functions are unit-testable without a DB or HTTP server. The use case
feeds in domain primitives (employee values, attendance records, holiday dates,
transactions) and receives fully-populated line-item values + warnings back.

All categorical enums are imported, never redefined (ADR-006):
* ``AttendanceStatus`` — owned by the attendance domain.
* ``SalaryType`` — owned by the employee domain.
* ``WeekDay`` — owned by ``app.shared.enums`` (the genuine cross-cutting enum).
* ``DivisorPolicy`` — owned by the business domain.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.domain.value_objects import AttendanceStatus
from app.features.business.domain.value_objects import DivisorPolicy
from app.features.employee.domain.value_objects import SalaryType
from app.features.payroll.domain.entities import PayrollLineItem, PayrollWarning
from app.features.payroll.domain.value_objects import (
    PayrollStatus,
    PayrollWarningType,
)
from app.shared.enums import WeekDay

# Python date.weekday(): 0=Monday..6=Sunday. WeekDay StrEnum members are in the
# same order, so their index maps 1:1.
_WEEKDAY_INDEX = {
    WeekDay.MONDAY: 0,
    WeekDay.TUESDAY: 1,
    WeekDay.WEDNESDAY: 2,
    WeekDay.THURSDAY: 3,
    WeekDay.FRIDAY: 4,
    WeekDay.SATURDAY: 5,
    WeekDay.SUNDAY: 6,
}

_ZERO = Decimal("0.00")
_QUANT = Decimal("0.01")  # NUMERIC(10,2) rounding


@dataclass(frozen=True)
class TransactionTotals:
    """Sums of transactions by direction (matches TransactionType ADDITION/DEDUCTION)."""

    additions: Decimal
    deductions: Decimal


def _q(value: Decimal) -> Decimal:
    """Quantize to 2 decimal places (NUMERIC(10,2), ROUND_HALF_UP)."""
    return value.quantize(_QUANT, rounding=ROUND_HALF_UP)


def calculate_ot_pay(
    daily_rate: Decimal, working_hours: Decimal, ot_hours: Decimal, multiplier: Decimal
) -> Decimal:
    """ot_pay = (daily_rate / working_hours) * overtime_hours * multiplier."""
    if working_hours <= 0 or ot_hours <= 0:
        return _ZERO
    return _q((daily_rate / working_hours) * ot_hours * multiplier)


def sum_transactions(transactions: list) -> TransactionTotals:
    """Sum transaction amounts by type into additions / deductions.

    ``transactions`` is a list of objects with ``.type`` (TransactionType) and
    ``.amount`` (Decimal). Typed loosely to avoid importing the transaction
    domain's entity — keeps the payroll domain dependent only on its own layer
    + the shared enums already imported.
    """
    additions = _ZERO
    deductions = _ZERO
    for t in transactions:
        if str(t.type) == "addition":
            additions += t.amount
        elif str(t.type) == "deduction":
            deductions += t.amount
    return TransactionTotals(additions=_q(additions), deductions=_q(deductions))


@dataclass(frozen=True)
class AttendanceSummary:
    present_days: Decimal
    half_days: Decimal
    paid_leave_days: Decimal
    unpaid_leave_days: Decimal
    holiday_days: int
    weekly_off_days_count: int
    overtime_hours: Decimal


def summarize_attendance(
    records: list[AttendanceRecord],
    weekly_off_days: list[WeekDay],
    paid_holiday_dates: set[date],
    year: int,
    month: int,
) -> AttendanceSummary:
    """Tally attendance counts for a month from explicit records + derived days.

    For each calendar day of the month: if an explicit attendance record exists
    it is counted by status (and its overtime hours accumulated); otherwise the
    day is derived — paid holidays count as a holiday day and weekly-off days
    are counted separately. Missing working days are NOT counted here; they
    surface as warnings via :func:`generate_warnings_for_line_item`.
    """
    _, days_in_month = calendar.monthrange(year, month)
    off_weekdays = {_WEEKDAY_INDEX[WeekDay(str(d))] for d in weekly_off_days}
    record_by_date: dict[date, AttendanceRecord] = {r.date: r for r in records}

    present = Decimal(0)
    half = Decimal(0)
    paid_leave = Decimal(0)
    unpaid_leave = Decimal(0)
    holidays = 0
    weekly_offs = 0
    ot_total = Decimal(0)

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        rec = record_by_date.get(d)
        if rec is not None:
            ot_total += rec.overtime_hours or _ZERO
            if rec.status == AttendanceStatus.PRESENT:
                present += Decimal(1)
            elif rec.status == AttendanceStatus.HALF_DAY:
                half += Decimal(1)
            elif rec.status == AttendanceStatus.PAID_LEAVE:
                paid_leave += Decimal(1)
            elif rec.status == AttendanceStatus.UNPAID_LEAVE:
                unpaid_leave += Decimal(1)
            continue
        # No explicit record — derive.
        if d in paid_holiday_dates:
            holidays += 1
        elif d.weekday() in off_weekdays:
            weekly_offs += 1
        # Missing working days are not counted here; they surface as warnings.

    return AttendanceSummary(
        present_days=_q(present),
        half_days=_q(half),
        paid_leave_days=_q(paid_leave),
        unpaid_leave_days=_q(unpaid_leave),
        holiday_days=holidays,
        weekly_off_days_count=weekly_offs,
        overtime_hours=_q(ot_total),
    )


def divisor_for(divisor_policy: str | None, year: int, month: int) -> int:
    """Resolve the monthly-salary divisor (PRODUCT.md → DivisorPolicy).

    Accepts the enum's string value (``"26"`` / ``"30"`` / ``"calendar"``) or
    ``None`` (defaults to ``26``).
    """
    value = divisor_policy or DivisorPolicy.TWENTY_SIX.value
    if value == DivisorPolicy.TWENTY_SIX.value:
        return 26
    if value == DivisorPolicy.THIRTY.value:
        return 30
    # calendar → actual days in the month
    _, days_in_month = calendar.monthrange(year, month)
    return days_in_month


def calculate_line_item_values(
    *,
    run_id: UUID,
    business_id: UUID,
    employee_id: UUID,
    employee_name: str,
    salary_type: str,
    base_rate: Decimal,
    divisor_policy: str | None,
    overtime_multiplier: Decimal,
    working_hours: Decimal,
    attendance: AttendanceSummary,
    transaction_totals: TransactionTotals,
    year: int,
    month: int,
) -> PayrollLineItem:
    """Compute all salary fields for a line item from attendance + transactions.

    Implements the three salary formulas in PRODUCT.md → Salary Formulas. Money
    is always Decimal; results quantized to NUMERIC(10,2). Net payable is
    ``earned + overtime_pay + additions − deductions``.
    """
    earned = _ZERO
    ot_pay = _ZERO

    if salary_type == SalaryType.MONTHLY.value:
        divisor = divisor_for(divisor_policy, year, month)
        daily_rate = base_rate / Decimal(divisor)
        paid_days = (
            attendance.present_days
            + (attendance.half_days * Decimal("0.5"))
            + attendance.paid_leave_days
            + Decimal(attendance.holiday_days)
        )
        earned = _q(daily_rate * paid_days)
        ot_pay = calculate_ot_pay(
            daily_rate, working_hours, attendance.overtime_hours, overtime_multiplier
        )
    elif salary_type == SalaryType.DAILY.value:
        daily_rate = base_rate
        earned = _q(
            daily_rate * attendance.present_days
            + (daily_rate * Decimal("0.5") * attendance.half_days)
        )
        ot_pay = calculate_ot_pay(
            daily_rate, working_hours, attendance.overtime_hours, overtime_multiplier
        )
    elif salary_type == SalaryType.HOURLY.value:
        # total hours worked = present full days + half days (prorated) + overtime hours.
        # Overtime is already folded into total_hours for hourly (no separate ot_pay).
        total_hours = (
            attendance.present_days * working_hours
            + (attendance.half_days * Decimal("0.5") * working_hours)
            + attendance.overtime_hours
        )
        earned = _q(base_rate * total_hours)
        ot_pay = _ZERO
    else:
        raise ValueError(f"Unknown salary_type: {salary_type}")

    net = _q(earned + ot_pay + transaction_totals.additions - transaction_totals.deductions)

    return PayrollLineItem.create(
        payroll_run_id=run_id,
        business_id=business_id,
        employee_id=employee_id,
        employee_name=employee_name,
        salary_type=salary_type,
        base_rate=_q(base_rate),
        divisor_policy_used=divisor_policy,
        overtime_multiplier_used=overtime_multiplier,
        working_hours_used=working_hours,
        present_days=attendance.present_days,
        half_days=attendance.half_days,
        paid_leave_days=attendance.paid_leave_days,
        unpaid_leave_days=attendance.unpaid_leave_days,
        holiday_days=attendance.holiday_days,
        weekly_off_days_count=attendance.weekly_off_days_count,
        overtime_hours=attendance.overtime_hours,
        earned_salary=earned,
        overtime_pay=ot_pay,
        total_additions=transaction_totals.additions,
        total_deductions=transaction_totals.deductions,
        net_payable=net,
        status=PayrollStatus.DRAFT,
        paid_via=None,
        paid_date=None,
    )


def generate_warnings_for_line_item(
    *,
    line_item_id: UUID,
    weekly_off_days: list[WeekDay],
    records: list[AttendanceRecord],
    paid_holiday_dates: set[date],
    year: int,
    month: int,
) -> list[PayrollWarning]:
    """Generate ``missing_attendance`` warnings for a line item.

    Loops calendar days; skips weekly-off days and paid holidays; any remaining
    working day with no explicit attendance record becomes a missing date. A
    single warning (covering all missing dates) is returned per line item.
    """
    _, days_in_month = calendar.monthrange(year, month)
    explicit_dates = {r.date for r in records}
    off_weekdays = {_WEEKDAY_INDEX[WeekDay(str(d))] for d in weekly_off_days}

    missing_dates: list[date] = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        if d.weekday() in off_weekdays:
            continue
        if d in paid_holiday_dates:
            continue
        if d not in explicit_dates:
            missing_dates.append(d)

    if not missing_dates:
        return []
    return [
        PayrollWarning.create(
            payroll_line_item_id=line_item_id,
            warning_type=PayrollWarningType.MISSING_ATTENDANCE,
            affected_dates=missing_dates,
            message=f"Attendance missing for {len(missing_dates)} working day(s)",
        )
    ]


__all__ = [
    "AttendanceSummary",
    "TransactionTotals",
    "calculate_line_item_values",
    "calculate_ot_pay",
    "divisor_for",
    "generate_warnings_for_line_item",
    "sum_transactions",
    "summarize_attendance",
]
