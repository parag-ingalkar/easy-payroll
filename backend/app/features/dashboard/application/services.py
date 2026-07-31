"""Dashboard application service — assembles the aggregate dashboard payload."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from app.features.attendance.domain.entities import AttendanceRecord
from app.features.attendance.domain.value_objects import AttendanceStatus
from app.features.business.domain.entities import Business
from app.features.employee.domain.entities import Employee
from app.features.payroll.domain.entities import PayrollLineItem, PayrollRun
from app.features.transaction.domain.entities import Transaction

if TYPE_CHECKING:
    from app.features.holiday.domain.entities import Holiday

MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

MONTH_SHORT = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class DashboardService:
    """Read-only service that assembles the dashboard aggregate."""

    business_service: BusinessServicePort
    employee_service: EmployeeServicePort
    attendance_service: AttendanceServicePort
    holiday_service: HolidayServicePort
    payroll_service: PayrollServicePort
    transaction_service: TransactionServicePort

    async def get_dashboard(self, business_id: UUID, owner_id: UUID) -> dict:
        business = await self.business_service.get_owned_business(business_id, owner_id)

        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        trend_start = today - timedelta(days=6)

        # Gather data in parallel where possible
        employees: Sequence[Employee] = await self.employee_service.list_by_business(business.id)
        active_employees = [e for e in employees if e.is_active]
        active_count = len(active_employees)

        # Today's attendance
        todays_attendance = await self.attendance_service.list_by_business_and_date(
            business.id, today
        )
        todays_att_by_status = _group_attendance(todays_attendance)
        present_today = todays_att_by_status.get(AttendanceStatus.PRESENT, 0)
        half_today = todays_att_by_status.get(AttendanceStatus.HALF_DAY, 0)
        on_leave_today = todays_att_by_status.get(
            AttendanceStatus.PAID_LEAVE, 0
        ) + todays_att_by_status.get(AttendanceStatus.UNPAID_LEAVE, 0)
        marked_today = len(todays_attendance)
        pending_attendance = max(0, active_count - marked_today)

        # Current month payroll run
        current_run = await self.payroll_service.get_by_business_and_period(
            business.id, today.year, today.month
        )

        if current_run:
            line_items = await self.payroll_service.list_line_items(current_run.id)
            total_payable = current_run.total_amount_due
            paid_count = sum(1 for li in line_items if li.status.value == "paid")
            total_count = len(line_items)
        else:
            total_payable = Decimal("0")
            paid_count = 0
            total_count = 0
        run_status = current_run.status.value if current_run else "not_run"

        # Monthly transactions
        transactions = await self._get_monthly_transactions(
            business.id, active_employees, month_start, month_end
        )
        monthly_additions = sum(
            (t.amount for t in transactions if t.type.value == "addition"), Decimal("0")
        )
        monthly_deductions = sum(
            (t.amount for t in transactions if t.type.value == "deduction"), Decimal("0")
        )

        # 7-day attendance trend
        trend = await self._build_trend(business.id, active_count, trend_start, today)

        # 6-month payroll history
        payroll_history = await self._build_payroll_history(business.id, today, active_count)

        # Projected monthly cost
        projected_monthly_cost = _project_cost(active_employees)

        # YTD paid
        ytd_paid = await self._ytd_paid(business.id, today.year)

        return {
            "business": {"name": business.name},
            "active_employees": active_count,
            "pending_attendance": pending_attendance,
            "present_today": present_today,
            "half_today": half_today,
            "on_leave_today": on_leave_today,
            "payroll": {
                "status": run_status,
                "total_payable": total_payable,
                "paid_count": paid_count,
                "total_count": total_count,
            },
            "monthly_additions": monthly_additions,
            "monthly_deductions": monthly_deductions,
            "month": today.month,
            "month_name": MONTH_NAMES[today.month - 1],
            "year": today.year,
            "trend": trend,
            "payroll_history": payroll_history,
            "projected_monthly_cost": projected_monthly_cost,
            "ytd_paid": ytd_paid,
        }

    async def _get_monthly_transactions(
        self,
        business_id: UUID,
        employees: list[Employee],
        start: date,
        end: date,
    ) -> list[Transaction]:
        all_txns: list[Transaction] = []
        for emp in employees:
            txns = await self.transaction_service.get_by_employee_and_date_range(emp.id, start, end)
            all_txns.extend(txns)
        return all_txns

    async def _build_trend(
        self,
        business_id: UUID,
        active_count: int,
        trend_start: date,
        today: date,
    ) -> list[dict]:
        """Build 7-day attendance trend by querying each day individually."""
        trend: list[dict] = []
        for i in range(7):
            day = trend_start + timedelta(days=i)
            records = await self.attendance_service.list_by_business_and_date(business_id, day)
            by_status = _group_attendance(records)
            present = by_status.get(AttendanceStatus.PRESENT, 0)
            half = by_status.get(AttendanceStatus.HALF_DAY, 0)
            leave = by_status.get(AttendanceStatus.PAID_LEAVE, 0) + by_status.get(
                AttendanceStatus.UNPAID_LEAVE, 0
            )
            marked = present + half + leave
            absent = max(0, active_count - marked)
            trend.append(
                {
                    "day": WEEKDAY_ABBR[day.weekday()],
                    "date": f"{day.day}/{day.month}",
                    "present": present,
                    "half": half,
                    "leave": leave,
                    "absent": absent,
                }
            )
        return trend

    async def _build_payroll_history(
        self,
        business_id: UUID,
        today: date,
        active_count: int,
    ) -> list[dict]:
        runs = await self.payroll_service.list_by_business(business_id)
        history: list[dict] = []
        for i in range(6):
            d = today - timedelta(days=i * 30)
            month, year = d.month, d.year
            run = next(
                (r for r in runs if r.year == year and r.month == month),
                None,
            )
            if run:
                items = await self.payroll_service.list_line_items(run.id)
                total = run.total_amount_due
                paid = sum(li.net_payable for li in items if li.status.value == "paid")
            else:
                total = Decimal("0")
                paid = Decimal("0")
            history.insert(
                0,
                {
                    "month": str(month),
                    "label": MONTH_SHORT[month - 1],
                    "total": total,
                    "paid": paid,
                },
            )
        return history

    async def _ytd_paid(self, business_id: UUID, year: int) -> Decimal:
        runs = await self.payroll_service.list_by_business(business_id)
        total = Decimal("0")
        for run in runs:
            if run.year == year:
                items = await self.payroll_service.list_line_items(run.id)
                for li in items:
                    if li.status.value == "paid":
                        total += li.net_payable
        return total


# --- Service port Protocols (structural subtyping) ---


class BusinessServicePort(Protocol):
    async def get_owned_business(self, business_id: UUID, owner_id: UUID) -> Business: ...


class EmployeeServicePort(Protocol):
    async def list_by_business(
        self, business_id: UUID, include_inactive: bool = False
    ) -> list[Employee]: ...


class AttendanceServicePort(Protocol):
    async def list_by_business_and_date(
        self, business_id: UUID, attendance_date: date
    ) -> Sequence[AttendanceRecord]: ...


class HolidayServicePort(Protocol):
    async def list_by_business(
        self, business_id: UUID, year: int | None = None, month: int | None = None
    ) -> Sequence[Holiday]: ...


class PayrollServicePort(Protocol):
    async def get_by_business_and_period(
        self, business_id: UUID, year: int, month: int
    ) -> PayrollRun | None: ...
    async def list_by_business(self, business_id: UUID) -> Sequence[PayrollRun]: ...
    async def list_line_items(self, run_id: UUID) -> Sequence[PayrollLineItem]: ...


class TransactionServicePort(Protocol):
    async def get_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[Transaction]: ...


# --- Helpers ---


def _group_attendance(records: Sequence[AttendanceRecord]) -> dict[AttendanceStatus, int]:
    counts: dict[AttendanceStatus, int] = {}
    for r in records:
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts


def _project_cost(employees: list[Employee]) -> Decimal:
    total = Decimal("0")
    for e in employees:
        if e.salary_type.value == "monthly":
            total += e.base_rate
        elif e.salary_type.value == "daily":
            total += e.base_rate * Decimal("30")
        else:  # hourly
            total += e.base_rate * e.working_hours * Decimal("30")
    return total
