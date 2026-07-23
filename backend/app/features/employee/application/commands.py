from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.features.auth.domain.entities import CurrentUser
from app.features.employee.domain.value_objects import SalaryType
from app.shared.enums import WeekDay


@dataclass(frozen=True)
class CreateEmployeeCommand:
    current_user: CurrentUser
    business_id: UUID
    name: str
    salary_type: SalaryType
    base_rate: Decimal
    phone: str | None
    designation: str | None
    joining_date: date | None
    overtime_multiplier: Decimal | None
    weekly_off_days: Sequence[WeekDay] | None
    working_hours: Decimal | None


@dataclass(frozen=True)
class UpdateEmployeeCommand:
    current_user: CurrentUser
    employee_id: UUID
    name: str | None = None
    salary_type: SalaryType | None = None
    base_rate: Decimal | None = None
    phone: str | None = None
    designation: str | None = None
    joining_date: date | None = None
    overtime_multiplier: Decimal | None = None
    weekly_off_days: Sequence[WeekDay] | None = None
    working_hours: Decimal | None = None


@dataclass(frozen=True)
class GetEmployeesCommand:
    current_user: CurrentUser
    business_id: UUID
    include_inactive: bool = False


@dataclass(frozen=True)
class GetEmployeeCommand:
    current_user: CurrentUser
    employee_id: UUID


@dataclass(frozen=True)
class DeleteEmployeeCommand:
    current_user: CurrentUser
    employee_id: UUID


@dataclass(frozen=True)
class ActivateEmployeeCommand:
    current_user: CurrentUser
    employee_id: UUID


@dataclass(frozen=True)
class DeactivateEmployeeCommand:
    current_user: CurrentUser
    employee_id: UUID
