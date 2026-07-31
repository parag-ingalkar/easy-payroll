from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import UUID

from app.features.attendance.domain.entities import AttendanceRecord
from app.features.business.domain.entities import Business
from app.features.employee.domain.entities import Employee
from app.features.holiday.domain.entities import Holiday
from app.features.payroll.domain.entities import (
    PayrollLineItem,
    PayrollRun,
    PayrollWarning,
)
from app.features.transaction.domain.entities import Transaction


class PayrollRepositoryPort(Protocol):
    """Protocol for the payroll repository."""

    async def get_run_by_id(self, run_id: UUID) -> PayrollRun | None:
        """Fetch a payroll run by its ID."""
        ...

    async def get_by_business_and_period(
        self, business_id: UUID, year: int, month: int
    ) -> PayrollRun | None:
        """Fetch a payroll run by business + (year, month) if one exists."""
        ...

    async def list_by_business(self, business_id: UUID) -> Sequence[PayrollRun]:
        """List payroll runs for a business (most recent first)."""
        ...

    async def add_run(self, run: PayrollRun) -> None:
        """Persist a new payroll run."""
        ...

    async def update_run(self, run: PayrollRun) -> None:
        """Update an existing payroll run (e.g. totals, status)."""
        ...

    async def delete_run(self, run: PayrollRun) -> None:
        """Delete a payroll run and its associated line items and warnings."""
        ...

    async def add_line_items(self, line_items: Sequence[PayrollLineItem]) -> None:
        """Persist all line items for a run."""
        ...

    async def add_warnings(self, warnings: Sequence[PayrollWarning]) -> None:
        """Persist all warnings for a run's line items."""
        ...

    async def list_line_items(self, run_id: UUID) -> Sequence[PayrollLineItem]:
        """List line items for a run."""
        ...

    async def get_line_item_by_id(self, line_item_id: UUID) -> PayrollLineItem | None:
        """Fetch a single line item by id."""
        ...

    async def update_line_items(self, line_items: Sequence[PayrollLineItem]) -> None:
        """Update existing line items (e.g. mark paid)."""
        ...

    async def list_warnings(self, run_id: UUID) -> Sequence[PayrollWarning]:
        """List all warnings attached to a run's line items."""
        ...


class BusinessServicePort(Protocol):
    """Cross-feature port for the payroll feature to access business capability."""

    async def get_owned_business(self, business_id: UUID, owner_id: UUID) -> Business:
        """Fetch a business and verify it is owned by ``owner_id``."""
        ...


class EmployeeServicePort(Protocol):
    """Cross-feature port for the payroll feature to access employee capability."""

    async def list_by_business(
        self, business_id: UUID, include_inactive: bool = False
    ) -> list[Employee]:
        """List employees belonging to a business."""
        ...


class AttendanceServicePort(Protocol):
    """Cross-feature port for the payroll feature to access attendance capability."""

    async def list_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> Sequence[AttendanceRecord]:
        """List attendance records for an employee within a date range (inclusive)."""
        ...


class HolidayServicePort(Protocol):
    """Cross-feature port for the payroll feature to access holiday capability."""

    async def list_by_business(
        self,
        business_id: UUID,
        year: int | None = None,
        month: int | None = None,
    ) -> Sequence[Holiday]:
        """List holidays for a business, optionally filtered by year/month."""
        ...


class TransactionServicePort(Protocol):
    """Cross-feature port for the payroll feature to access transaction capability."""

    async def get_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[Transaction]:
        """Fetch transactions for an employee within a date range (inclusive)."""
        ...
