"""Payroll-domain entities — pure Python dataclasses."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.features.payroll.domain.exceptions import (
    PayrollAlreadyFinalizedError,
    PayrollRunNotOwnedError,
)
from app.features.payroll.domain.value_objects import (
    PayrollStatus,
    PayrollWarningType,
)


@dataclass
class PayrollRun:
    """A single payroll run for a business for a given (year, month).

    One business can have at most one payroll run per month (uniqueness is
    enforced at the database level on ``(business_id, year, month)``). A run
    aggregates many :class:`PayrollLineItem` rows (one per active employee) and
    a high-level summary: total amount due and a roll-up ``is_warning`` flag
    that is true if any line item carries a warning.
    """

    id: UUID
    business_id: UUID
    month: int
    year: int
    status: PayrollStatus
    total_amount_due: Decimal
    is_warning: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, *, business_id: UUID, month: int, year: int) -> "PayrollRun":
        """Factory for a new draft payroll run (empty summary)."""
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            business_id=business_id,
            month=month,
            year=year,
            status=PayrollStatus.DRAFT,
            total_amount_due=Decimal("0"),
            is_warning=False,
            created_at=now,
            updated_at=now,
        )

    def set_summary(self, *, total_amount_due: Decimal, is_warning: bool) -> None:
        """Update the roll-up totals after line items have been computed."""
        self.total_amount_due = total_amount_due
        self.is_warning = is_warning
        self.updated_at = datetime.now(UTC)

    def finalize(self) -> None:
        """Transition the run from DRAFT to FINALIZED (idempotent-safe)."""
        if self.status == PayrollStatus.FINALIZED:
            raise PayrollAlreadyFinalizedError(payroll_id=self.id)
        self.status = PayrollStatus.FINALIZED
        self.updated_at = datetime.now(UTC)

    def ensure_owned_by_business(self, business_id: UUID) -> None:
        """Ensure that the run belongs to the given business."""
        if self.business_id != business_id:
            raise PayrollRunNotOwnedError(payroll_id=self.id, business_id=business_id)


@dataclass
class PayrollLineItem:
    """The computed payroll for one employee for one month.

    Holds the per-employee salary calculation: the attendance counts tallied
    for the period, the earned salary and overtime pay, the transaction
    totals, and the resulting net payable. The ``*_used`` fields snapshot the
    employee/business values used for the calculation so the slip is
    self-describing even if the source rows later change.
    """

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
    # Attendance tallies for the period
    present_days: Decimal
    half_days: Decimal
    paid_leave_days: Decimal
    unpaid_leave_days: Decimal
    holiday_days: int
    weekly_off_days_count: int
    overtime_hours: Decimal
    # Computed amounts
    earned_salary: Decimal
    overtime_pay: Decimal
    total_additions: Decimal
    total_deductions: Decimal
    net_payable: Decimal
    # Lifecycle
    status: PayrollStatus
    paid_via: str | None
    paid_date: date | None

    @classmethod
    def create(
        cls,
        *,
        payroll_run_id: UUID,
        business_id: UUID,
        employee_id: UUID,
        employee_name: str,
        salary_type: str,
        base_rate: Decimal,
        divisor_policy_used: str | None,
        overtime_multiplier_used: Decimal,
        working_hours_used: Decimal,
        present_days: Decimal,
        half_days: Decimal,
        paid_leave_days: Decimal,
        unpaid_leave_days: Decimal,
        holiday_days: int,
        weekly_off_days_count: int,
        overtime_hours: Decimal,
        earned_salary: Decimal,
        overtime_pay: Decimal,
        total_additions: Decimal,
        total_deductions: Decimal,
        net_payable: Decimal,
        status: PayrollStatus = PayrollStatus.DRAFT,
        paid_via: str | None = None,
        paid_date: date | None = None,
    ) -> "PayrollLineItem":
        """Factory for a new line item."""
        return cls(
            id=uuid4(),
            payroll_run_id=payroll_run_id,
            business_id=business_id,
            employee_id=employee_id,
            employee_name=employee_name,
            salary_type=salary_type,
            base_rate=base_rate,
            divisor_policy_used=divisor_policy_used,
            overtime_multiplier_used=overtime_multiplier_used,
            working_hours_used=working_hours_used,
            present_days=present_days,
            half_days=half_days,
            paid_leave_days=paid_leave_days,
            unpaid_leave_days=unpaid_leave_days,
            holiday_days=holiday_days,
            weekly_off_days_count=weekly_off_days_count,
            overtime_hours=overtime_hours,
            earned_salary=earned_salary,
            overtime_pay=overtime_pay,
            total_additions=total_additions,
            total_deductions=total_deductions,
            net_payable=net_payable,
            status=status,
            paid_via=paid_via,
            paid_date=paid_date,
        )


@dataclass
class PayrollWarning:
    """A warning attached to a payroll line item (e.g. missing attendance)."""

    id: UUID
    payroll_line_item_id: UUID
    warning_type: PayrollWarningType
    affected_dates: list[date]
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        *,
        payroll_line_item_id: UUID,
        warning_type: PayrollWarningType,
        affected_dates: Sequence[date],
        message: str,
    ) -> "PayrollWarning":
        """Factory for a new payroll warning."""
        return cls(
            id=uuid4(),
            payroll_line_item_id=payroll_line_item_id,
            warning_type=warning_type,
            affected_dates=list(affected_dates),
            message=message,
        )


__all__ = [
    "PayrollLineItem",
    "PayrollRun",
    "PayrollWarning",
]
