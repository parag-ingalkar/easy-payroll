"""Unit tests for the payroll calculation engine (pure Python, no DB/HTTP).

Covers: monthly/daily/hourly earned formulas, overtime pay, divisor policies,
attendance tallying (incl. holiday + weekly-off derivation), transaction
summing, and warning generation (missing working days only).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.domain.value_objects import AttendanceStatus
from app.features.business.domain.value_objects import DivisorPolicy
from app.features.employee.domain.value_objects import SalaryType
from app.features.payroll.domain.entities import PayrollLineItem
from app.features.payroll.domain.services import (
    AttendanceSummary,
    TransactionTotals,
    calculate_line_item_values,
    calculate_ot_pay,
    divisor_for,
    generate_warnings_for_line_item,
    sum_transactions,
    summarize_attendance,
)
from app.shared.enums import WeekDay

_YEAR = 2026
_MONTH = 2  # 28 days (2026 is not a leap year); weekdays/offs: see below


def _rec(d: date, status: AttendanceStatus, ot: str = "0") -> AttendanceRecord:
    return AttendanceRecord.create(
        employee_id=uuid4(), date=d, status=status, overtime_hours=Decimal(ot)
    )


# --- calculate_ot_pay ------------------------------------------------------


def test_ot_pay_basic_formula():
    # (daily_rate / working_hours) * ot_hours * multiplier
    assert calculate_ot_pay(Decimal("1000"), Decimal(8), Decimal(2), Decimal("2")) == Decimal(
        "500.00"
    )


def test_ot_pay_zero_when_no_overtime():
    assert calculate_ot_pay(Decimal("1000"), Decimal(8), Decimal(0), Decimal("2")) == Decimal(
        "0.00"
    )


def test_ot_pay_zero_when_no_working_hours():
    assert calculate_ot_pay(Decimal("1000"), Decimal(0), Decimal(2), Decimal("2")) == Decimal(
        "0.00"
    )


# --- divisor_for -----------------------------------------------------------


def test_divisor_policies():
    assert divisor_for(DivisorPolicy.TWENTY_SIX.value, _YEAR, _MONTH) == 26
    assert divisor_for(DivisorPolicy.THIRTY.value, _YEAR, _MONTH) == 30
    # Feb 2026 has 28 days
    assert divisor_for(DivisorPolicy.CALENDAR.value, _YEAR, _MONTH) == 28


def test_divisor_defaults_to_26_when_none():
    assert divisor_for(None, _YEAR, _MONTH) == 26


# --- sum_transactions ------------------------------------------------------


@dataclass
class _Txn:
    type: object
    amount: Decimal


def test_sum_transactions_buckets_by_direction():
    totals = sum_transactions(
        [
            _Txn(type="addition", amount=Decimal("100")),
            _Txn(type="addition", amount=Decimal("50.25")),
            _Txn(type="deduction", amount=Decimal("30")),
        ]
    )
    assert totals.additions == Decimal("150.25")
    assert totals.deductions == Decimal("30.00")


def test_sum_transactions_empty():
    totals = sum_transactions([])
    assert totals.additions == Decimal("0.00")
    assert totals.deductions == Decimal("0.00")


# --- summarize_attendance --------------------------------------------------


def test_summarize_attendance_counts_and_derives_holiday_and_weekly_off():
    # Feb 2026: the 1st is a Sunday (off). Mark Feb 2 (Mon) present, Feb 3 (Tue)
    # half-day, Feb 4 (Wed) paid-leave, Feb 5 (Thu) unpaid-leave. Feb 6 (Fri) is
    # a paid holiday (no record). Feb 7 (Sat) is an off (Sunday weekly-off).
    weekly_offs = [WeekDay.SUNDAY]
    paid_holidays = {date(_YEAR, _MONTH, 6)}
    records = [
        _rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT, ot="2"),
        _rec(date(_YEAR, _MONTH, 3), AttendanceStatus.HALF_DAY),
        _rec(date(_YEAR, _MONTH, 4), AttendanceStatus.PAID_LEAVE),
        _rec(date(_YEAR, _MONTH, 5), AttendanceStatus.UNPAID_LEAVE),
    ]
    summary = summarize_attendance(records, weekly_offs, paid_holidays, _YEAR, _MONTH)

    assert summary.present_days == Decimal("1.00")
    assert summary.half_days == Decimal("1.00")
    assert summary.paid_leave_days == Decimal("1.00")
    assert summary.unpaid_leave_days == Decimal("1.00")
    assert summary.holiday_days == 1
    assert summary.overtime_hours == Decimal("2.00")
    # Feb 2026 has 4 Sundays (1st, 8th, 15th, 22nd)
    assert summary.weekly_off_days_count == 4


# --- calculate_line_item_values -------------------------------------------


def _make_line_item(
    *,
    salary_type: str = SalaryType.MONTHLY.value,
    base_rate: Decimal = Decimal("26000"),
    divisor_policy: str | None = DivisorPolicy.TWENTY_SIX.value,
    overtime_multiplier: Decimal = Decimal("2"),
    working_hours: Decimal = Decimal(8),
    attendance: AttendanceSummary | None = None,
    transaction_totals: TransactionTotals | None = None,
) -> PayrollLineItem:
    """Typed builder around ``calculate_line_item_values`` with sane defaults.

    Replaces a dict-splat helper (which lost per-argument typing) with a proper
    keyword-typed wrapper so pyright can check the call sites.
    """
    return calculate_line_item_values(
        run_id=uuid4(),
        business_id=uuid4(),
        employee_id=uuid4(),
        employee_name="Test Employee",
        salary_type=salary_type,
        base_rate=base_rate,
        divisor_policy=divisor_policy,
        overtime_multiplier=overtime_multiplier,
        working_hours=working_hours,
        attendance=attendance or summarize_attendance([], [WeekDay.SUNDAY], set(), _YEAR, _MONTH),
        transaction_totals=transaction_totals or sum_transactions([]),
        year=_YEAR,
        month=_MONTH,
    )


def test_monthly_earned_with_present_days_and_overtime():
    # 1 present day, 26 divisor, overtime 2h
    summary = summarize_attendance(
        [_rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT, ot="2")],
        [WeekDay.SUNDAY],
        set(),
        _YEAR,
        _MONTH,
    )
    item = _make_line_item(attendance=summary)
    # daily_rate = 26000/26 = 1000; earned = 1000 * 1 = 1000
    assert item.earned_salary == Decimal("1000.00")
    # ot = (1000/8)*2*2 = 500
    assert item.overtime_pay == Decimal("500.00")
    assert item.net_payable == Decimal("1500.00")


def test_monthly_paid_days_include_half_paid_leave_and_holidays():
    # present 1 + half 1 (0.5) + paid_leave 1 + holiday 1 => 3.5 paid days
    summary = summarize_attendance(
        [
            _rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT),
            _rec(date(_YEAR, _MONTH, 3), AttendanceStatus.HALF_DAY),
            _rec(date(_YEAR, _MONTH, 4), AttendanceStatus.PAID_LEAVE),
        ],
        [WeekDay.SUNDAY],
        {date(_YEAR, _MONTH, 6)},  # holiday counted as a paid day
        _YEAR,
        _MONTH,
    )
    item = _make_line_item(attendance=summary)
    # daily_rate=1000; paid_days = 1 + 0.5 + 1 + 1 = 3.5; earned = 3500
    assert item.earned_salary == Decimal("3500.00")


def test_daily_salary_earned():
    summary = summarize_attendance(
        [
            _rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT),
            _rec(date(_YEAR, _MONTH, 3), AttendanceStatus.HALF_DAY),
        ],
        [WeekDay.SUNDAY],
        set(),
        _YEAR,
        _MONTH,
    )
    item = _make_line_item(
        salary_type=SalaryType.DAILY.value,
        base_rate=Decimal("500"),  # daily_rate = base_rate
        attendance=summary,
    )
    # earned = 500*1 + 500*0.5*1 = 750
    assert item.earned_salary == Decimal("750.00")


def test_hourly_salary_earned_includes_overtime_in_total_hours():
    summary = summarize_attendance(
        [_rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT, ot="2")],
        [WeekDay.SUNDAY],
        set(),
        _YEAR,
        _MONTH,
    )
    item = _make_line_item(
        salary_type=SalaryType.HOURLY.value,
        base_rate=Decimal("100"),  # hourly rate
        working_hours=Decimal(8),
        attendance=summary,
    )
    # total_hours = 1*8 + 0 + 2 = 10; earned = 100*10 = 1000; ot_pay = 0
    assert item.earned_salary == Decimal("1000.00")
    assert item.overtime_pay == Decimal("0.00")


def test_net_payable_applies_additions_and_deductions():
    summary = summarize_attendance(
        [_rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT)],
        [WeekDay.SUNDAY],
        set(),
        _YEAR,
        _MONTH,
    )
    totals = sum_transactions(
        [_Txn(type="addition", amount=Decimal("200")), _Txn(type="deduction", amount=Decimal("50"))]
    )
    item = _make_line_item(attendance=summary, transaction_totals=totals)
    # earned 1000 + ot 0 + additions 200 - deductions 50 = 1150
    assert item.total_additions == Decimal("200.00")
    assert item.total_deductions == Decimal("50.00")
    assert item.net_payable == Decimal("1150.00")


def test_line_item_snapshots_divisor_and_employee_values():
    summary = summarize_attendance([], [WeekDay.SUNDAY], set(), _YEAR, _MONTH)
    item = _make_line_item(attendance=summary)
    assert item.divisor_policy_used == DivisorPolicy.TWENTY_SIX.value
    assert item.overtime_multiplier_used == Decimal("2")
    assert item.working_hours_used == Decimal(8)
    assert item.employee_name == "Test Employee"


# --- generate_warnings_for_line_item --------------------------------------


def test_warning_lists_missing_working_days_only():
    # Feb 2026, weekly-off = Sunday. Provide NO records; expect every non-Sunday
    # non-holiday day to be flagged.
    warnings = generate_warnings_for_line_item(
        line_item_id=uuid4(),
        weekly_off_days=[WeekDay.SUNDAY],
        records=[],
        paid_holiday_dates=set(),
        year=_YEAR,
        month=_MONTH,
    )
    assert len(warnings) == 1
    w = warnings[0]
    # Feb 2026 has 28 days, 4 Sundays => 24 working days missing
    assert len(w.affected_dates) == 24
    assert w.affected_dates[0] == date(_YEAR, _MONTH, 2)  # first non-Sunday


def test_warning_skips_holidays_and_weekly_offs():
    # A paid holiday and a weekly-off should NOT appear as missing.
    warnings = generate_warnings_for_line_item(
        line_item_id=uuid4(),
        weekly_off_days=[WeekDay.SUNDAY],
        records=[_rec(date(_YEAR, _MONTH, 2), AttendanceStatus.PRESENT)],
        paid_holiday_dates={date(_YEAR, _MONTH, 6)},
        year=_YEAR,
        month=_MONTH,
    )
    assert len(warnings) == 1
    flagged = set(warnings[0].affected_dates)
    assert date(_YEAR, _MONTH, 6) not in flagged  # holiday skipped
    assert date(_YEAR, _MONTH, 1) not in flagged  # Sunday skipped


def test_no_warning_when_all_working_days_have_records():
    # Provide a record for every non-Sunday, non-holiday day in Feb 2026.
    all_working = [
        d
        for day in range(1, 29)
        for d in [date(_YEAR, _MONTH, day)]
        if d.weekday() != 6 and d != date(_YEAR, _MONTH, 6)
    ]
    records = [_rec(d, AttendanceStatus.PRESENT) for d in all_working]
    warnings = generate_warnings_for_line_item(
        line_item_id=uuid4(),
        weekly_off_days=[WeekDay.SUNDAY],
        records=records,
        paid_holiday_dates={date(_YEAR, _MONTH, 6)},
        year=_YEAR,
        month=_MONTH,
    )
    assert warnings == []
