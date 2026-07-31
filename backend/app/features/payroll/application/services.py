from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from app.features.payroll.application.ports import PayrollRepositoryPort
from app.features.payroll.domain.entities import (
    PayrollLineItem,
    PayrollRun,
    PayrollWarning,
)
from app.features.payroll.domain.exceptions import (
    PayrollLineItemNotFoundError,
    PayrollRunNotFoundError,
)


@dataclass
class PayrollService:
    """Application service — the sole gateway to ``PayrollRepositoryPort``."""

    payroll_repo: PayrollRepositoryPort

    async def get_run_by_id_or_raise(self, run_id: UUID) -> PayrollRun:
        """Fetch a run by id, raising ``PayrollRunNotFoundError`` if absent."""
        run = await self.payroll_repo.get_run_by_id(run_id)
        if not run:
            raise PayrollRunNotFoundError(payroll_id=run_id)
        return run

    async def get_by_business_and_period(
        self, business_id: UUID, year: int, month: int
    ) -> PayrollRun | None:
        return await self.payroll_repo.get_by_business_and_period(business_id, year, month)

    async def list_by_business(self, business_id: UUID) -> Sequence[PayrollRun]:
        return await self.payroll_repo.list_by_business(business_id)

    async def add_run(self, run: PayrollRun) -> None:
        await self.payroll_repo.add_run(run)

    async def update_run(self, run: PayrollRun) -> None:
        await self.payroll_repo.update_run(run)

    async def add_line_items(self, line_items: Sequence[PayrollLineItem]) -> None:
        await self.payroll_repo.add_line_items(line_items)

    async def add_warnings(self, warnings: Sequence[PayrollWarning]) -> None:
        await self.payroll_repo.add_warnings(warnings)

    async def list_line_items(self, run_id: UUID) -> Sequence[PayrollLineItem]:
        return await self.payroll_repo.list_line_items(run_id)

    async def get_line_item_by_id_or_raise(self, line_item_id: UUID) -> PayrollLineItem:
        """Fetch a line item by id, raising ``PayrollLineItemNotFoundError`` if absent."""
        item = await self.payroll_repo.get_line_item_by_id(line_item_id)
        if not item:
            raise PayrollLineItemNotFoundError(line_item_id=line_item_id)
        return item

    async def update_line_items(self, line_items: Sequence[PayrollLineItem]) -> None:
        await self.payroll_repo.update_line_items(line_items)

    async def list_warnings(self, run_id: UUID) -> Sequence[PayrollWarning]:
        return await self.payroll_repo.list_warnings(run_id)
