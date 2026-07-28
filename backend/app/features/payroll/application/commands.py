from dataclasses import dataclass
from uuid import UUID

from app.features.auth.domain.entities import CurrentUser


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
