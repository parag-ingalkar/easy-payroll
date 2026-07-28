"""Employee-domain entities — pure Python dataclasses."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.features.employee.domain.exceptions import (
    EmployeeAlreadyActiveError,
    EmployeeAlreadyInactiveError,
    EmployeeNotOwnedError,
)
from app.features.employee.domain.value_objects import SalaryType
from app.shared.enums import WeekDay
from app.shared.utils import get_weekday


@dataclass
class Employee:
    """A worker belonging to a business.

    Per ADR-015 / ADR-018, ``overtime_multiplier``, ``weekly_off_days`` and
    ``working_hours`` are **always populated** — copied from the business
    defaults at creation if not explicitly provided, and stored permanently on
    this row. There is no runtime resolution join to the business table during
    payroll or attendance calculation.

    ``designation`` is nullable free-text shown on the salary slip and employee
    list; it carries no payroll logic.
    """

    id: UUID
    business_id: UUID
    name: str
    salary_type: SalaryType
    base_rate: Decimal
    overtime_multiplier: Decimal
    weekly_off_days: Sequence[WeekDay]
    working_hours: Decimal
    phone: str | None
    designation: str | None
    joining_date: date | None
    created_at: datetime
    is_active: bool

    @classmethod
    def create(
        cls,
        *,
        business_id: UUID,
        name: str,
        salary_type: SalaryType,
        base_rate: Decimal,
        overtime_multiplier: Decimal | None,
        weekly_off_days: Sequence[WeekDay] | None,
        working_hours: Decimal | None,
        phone: str | None = None,
        designation: str | None = None,
        joining_date: date | None = None,
    ) -> "Employee":
        """Factory method for creating a new employee entity."""
        return cls(
            id=uuid4(),
            business_id=business_id,
            name=name,
            salary_type=salary_type,
            base_rate=base_rate,
            overtime_multiplier=overtime_multiplier or Decimal("2.0"),
            weekly_off_days=weekly_off_days or [WeekDay.SUNDAY],
            working_hours=working_hours or Decimal("8.0"),
            phone=phone,
            designation=designation,
            joining_date=joining_date,
            created_at=datetime.now(),
            is_active=True,
        )

    def update(
        self,
        *,
        name: str | None = None,
        salary_type: SalaryType | None = None,
        base_rate: Decimal | None = None,
        overtime_multiplier: Decimal | None = None,
        weekly_off_days: Sequence[WeekDay] | None = None,
        working_hours: Decimal | None = None,
        phone: str | None = None,
        designation: str | None = None,
        joining_date: date | None = None,
    ):
        """Update the employee entity with the given keyword arguments."""
        if name is not None:
            self.name = name
        if salary_type is not None:
            self.salary_type = salary_type
        if base_rate is not None:
            self.base_rate = base_rate
        if overtime_multiplier is not None:
            self.overtime_multiplier = overtime_multiplier
        if weekly_off_days is not None:
            self.weekly_off_days = weekly_off_days
        if working_hours is not None:
            self.working_hours = working_hours
        if phone is not None:
            self.phone = phone
        if designation is not None:
            self.designation = designation
        if joining_date is not None:
            self.joining_date = joining_date

    def deactivate(self):
        """Deactivate the employee."""
        if not self.is_active:
            raise EmployeeAlreadyInactiveError(employee_id=self.id)
        self.is_active = False

    def activate(self):
        """Activate the employee."""
        if self.is_active:
            raise EmployeeAlreadyActiveError(employee_id=self.id)
        self.is_active = True

    def ensure_belongs_to_business(self, business_id: UUID):
        """Ensure that the employee belongs to the given business."""
        if self.business_id != business_id:
            raise EmployeeNotOwnedError(employee_id=self.id, business_id=business_id)

    def is_date_weekly_off(self, date: date) -> bool:
        return any(day == get_weekday(date) for day in self.weekly_off_days)
