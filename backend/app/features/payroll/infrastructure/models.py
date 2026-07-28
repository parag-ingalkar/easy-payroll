"""SQLAlchemy ORM models for the payroll domain.

Three tables form the payroll persistence shape:

* ``payroll_runs`` — one row per (business, year, month); unique on that triple.
* ``payroll_line_items`` — one row per employee per run; cascades from the run
  and is also keyed back to ``employees`` for cross-run queries.
* ``payroll_warnings`` — zero or more warnings per line item; cascades from it.

Money is stored as ``Numeric(12,2)`` to accommodate large monthly totals; counts
are ``Integer``/``Numeric`` as appropriate. Two enum types are defined at module
scope so the migration and the ORM columns share one definition.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.features.payroll.domain.entities import (
    PayrollLineItem,
    PayrollRun,
    PayrollWarning,
)
from app.features.payroll.domain.value_objects import (
    PayrollStatus,
    PayrollWarningType,
)

payroll_status_enum = SAEnum(
    PayrollStatus,
    name="payroll_status_enum",
    values_callable=lambda x: [e.value for e in x],
)

payroll_warning_type_enum = SAEnum(
    PayrollWarningType,
    name="payroll_warning_type_enum",
    values_callable=lambda x: [e.value for e in x],
)


class PayrollRunModel(Base):
    """A payroll run for a business for a given (year, month).

    Uniqueness on ``(business_id, year, month)`` is enforced by
    ``uq_payroll_runs_business_period`` — a business can run payroll for a
    month at most once.
    """

    __tablename__ = "payroll_runs"
    __table_args__ = (
        UniqueConstraint("business_id", "year", "month", name="uq_payroll_runs_business_period"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PayrollStatus] = mapped_column(payroll_status_enum, nullable=False)
    total_amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_warning: Mapped[bool] = mapped_column(nullable=False, default=False, server_default="false")
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
    def from_domain(cls, run: PayrollRun) -> "PayrollRunModel":
        return cls(
            id=run.id,
            business_id=run.business_id,
            month=run.month,
            year=run.year,
            status=run.status,
            total_amount_due=run.total_amount_due,
            is_warning=run.is_warning,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )

    def to_domain(self) -> PayrollRun:
        return PayrollRun(
            id=self.id,
            business_id=self.business_id,
            month=self.month,
            year=self.year,
            status=self.status,
            total_amount_due=self.total_amount_due,
            is_warning=self.is_warning,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class PayrollLineItemModel(Base):
    """The computed payroll for one employee for one run."""

    __tablename__ = "payroll_line_items"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    salary_type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    divisor_policy_used: Mapped[str | None] = mapped_column(String(20), nullable=True)
    overtime_multiplier_used: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    working_hours_used: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    # Attendance tallies for the period
    present_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    half_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    paid_leave_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    unpaid_leave_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    holiday_days: Mapped[int] = mapped_column(Integer, nullable=False)
    weekly_off_days_count: Mapped[int] = mapped_column(Integer, nullable=False)
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    # Computed amounts
    earned_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    overtime_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_additions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_payable: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # Lifecycle
    status: Mapped[PayrollStatus] = mapped_column(payroll_status_enum, nullable=False)
    paid_via: Mapped[str | None] = mapped_column(String(50), nullable=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    @classmethod
    def from_domain(cls, item: PayrollLineItem) -> "PayrollLineItemModel":
        return cls(
            id=item.id,
            payroll_run_id=item.payroll_run_id,
            business_id=item.business_id,
            employee_id=item.employee_id,
            employee_name=item.employee_name,
            salary_type=item.salary_type,
            base_rate=item.base_rate,
            divisor_policy_used=item.divisor_policy_used,
            overtime_multiplier_used=item.overtime_multiplier_used,
            working_hours_used=item.working_hours_used,
            present_days=item.present_days,
            half_days=item.half_days,
            paid_leave_days=item.paid_leave_days,
            unpaid_leave_days=item.unpaid_leave_days,
            holiday_days=item.holiday_days,
            weekly_off_days_count=item.weekly_off_days_count,
            overtime_hours=item.overtime_hours,
            earned_salary=item.earned_salary,
            overtime_pay=item.overtime_pay,
            total_additions=item.total_additions,
            total_deductions=item.total_deductions,
            net_payable=item.net_payable,
            status=item.status,
            paid_via=item.paid_via,
            paid_date=item.paid_date,
        )

    def to_domain(self) -> PayrollLineItem:
        return PayrollLineItem(
            id=self.id,
            payroll_run_id=self.payroll_run_id,
            business_id=self.business_id,
            employee_id=self.employee_id,
            employee_name=self.employee_name,
            salary_type=self.salary_type,
            base_rate=self.base_rate,
            divisor_policy_used=self.divisor_policy_used,
            overtime_multiplier_used=self.overtime_multiplier_used,
            working_hours_used=self.working_hours_used,
            present_days=self.present_days,
            half_days=self.half_days,
            paid_leave_days=self.paid_leave_days,
            unpaid_leave_days=self.unpaid_leave_days,
            holiday_days=self.holiday_days,
            weekly_off_days_count=self.weekly_off_days_count,
            overtime_hours=self.overtime_hours,
            earned_salary=self.earned_salary,
            overtime_pay=self.overtime_pay,
            total_additions=self.total_additions,
            total_deductions=self.total_deductions,
            net_payable=self.net_payable,
            status=self.status,
            paid_via=self.paid_via,
            paid_date=self.paid_date,
        )


class PayrollWarningModel(Base):
    """A warning attached to a payroll line item (e.g. missing attendance)."""

    __tablename__ = "payroll_warnings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payroll_line_item_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll_line_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warning_type: Mapped[PayrollWarningType] = mapped_column(
        payroll_warning_type_enum, nullable=False
    )
    affected_dates: Mapped[list[date]] = mapped_column(ARRAY(Date), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    @classmethod
    def from_domain(cls, warning: PayrollWarning) -> "PayrollWarningModel":
        return cls(
            id=warning.id,
            payroll_line_item_id=warning.payroll_line_item_id,
            warning_type=warning.warning_type,
            affected_dates=warning.affected_dates,
            message=warning.message,
            created_at=warning.created_at,
        )

    def to_domain(self) -> PayrollWarning:
        return PayrollWarning(
            id=self.id,
            payroll_line_item_id=self.payroll_line_item_id,
            warning_type=self.warning_type,
            affected_dates=self.affected_dates,
            message=self.message,
            created_at=self.created_at,
        )
