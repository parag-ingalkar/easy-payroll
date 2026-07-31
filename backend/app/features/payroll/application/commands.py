from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.features.auth.domain.entities import CurrentUser
from app.features.payroll.domain.value_objects import PaymentMethod


@dataclass(frozen=True)
class CreatePayrollRunCommand:
    """Run payroll for a business for a given (year, month)."""

    current_user: CurrentUser
    business_id: UUID
    month: int
    year: int


@dataclass(frozen=True)
class GetPayrollRunCommand:
    current_user: CurrentUser
    business_id: UUID
    payroll_id: UUID


@dataclass(frozen=True)
class ListPayrollRunsCommand:
    current_user: CurrentUser
    business_id: UUID


@dataclass(frozen=True)
class FinalizePayrollRunCommand:
    current_user: CurrentUser
    business_id: UUID
    payroll_id: UUID


@dataclass(frozen=True)
class MarkLineItemPaidCommand:
    """Mark a single payroll line item as paid."""

    current_user: CurrentUser
    business_id: UUID
    payroll_id: UUID
    line_item_id: UUID
    paid_via: PaymentMethod
    paid_date: date


@dataclass(frozen=True)
class MarkAllPaidCommand:
    """Mark every line item in a run as paid with the same method."""

    current_user: CurrentUser
    business_id: UUID
    payroll_id: UUID
    paid_via: PaymentMethod
    paid_date: date
