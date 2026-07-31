from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.payroll.application.ports import PayrollRepositoryPort
from app.features.payroll.domain.entities import (
    PayrollLineItem,
    PayrollRun,
    PayrollWarning,
)
from app.features.payroll.infrastructure.models import (
    PayrollLineItemModel,
    PayrollRunModel,
    PayrollWarningModel,
)


class SQLPayrollRepository(PayrollRepositoryPort):
    """SQLAlchemy implementation of the payroll repository.

    Warnings are attached to line items (not directly to runs), so
    :meth:`list_warnings` joins ``payroll_warnings`` through
    ``payroll_line_items`` to collect every warning belonging to a run.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_run_by_id(self, run_id: UUID) -> PayrollRun | None:
        """Fetch a payroll run by its ID."""
        result = await self.session.get(PayrollRunModel, run_id)
        return result.to_domain() if result else None

    async def get_by_business_and_period(
        self, business_id: UUID, year: int, month: int
    ) -> PayrollRun | None:
        """Fetch a payroll run by business + (year, month) if one exists."""
        result = await self.session.execute(
            select(PayrollRunModel).where(
                PayrollRunModel.business_id == business_id,
                PayrollRunModel.year == year,
                PayrollRunModel.month == month,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_by_business(self, business_id: UUID) -> Sequence[PayrollRun]:
        """List payroll runs for a business (most recent first)."""
        result = await self.session.execute(
            select(PayrollRunModel)
            .where(PayrollRunModel.business_id == business_id)
            .order_by(
                PayrollRunModel.year.desc(),
                PayrollRunModel.month.desc(),
            )
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def add_run(self, run: PayrollRun) -> None:
        """Persist a new payroll run."""
        self.session.add(PayrollRunModel.from_domain(run))
        await self.session.flush()

    async def update_run(self, run: PayrollRun) -> None:
        """Update an existing payroll run (e.g. totals, status)."""
        await self.session.merge(PayrollRunModel.from_domain(run))
        await self.session.flush()

    async def add_line_items(self, line_items: Sequence[PayrollLineItem]) -> None:
        """Persist all line items for a run."""
        self.session.add_all([PayrollLineItemModel.from_domain(item) for item in line_items])
        await self.session.flush()

    async def add_warnings(self, warnings: Sequence[PayrollWarning]) -> None:
        """Persist all warnings for a run's line items."""
        self.session.add_all([PayrollWarningModel.from_domain(w) for w in warnings])
        await self.session.flush()

    async def list_line_items(self, run_id: UUID) -> Sequence[PayrollLineItem]:
        """List line items for a run."""
        result = await self.session.execute(
            select(PayrollLineItemModel)
            .where(PayrollLineItemModel.payroll_run_id == run_id)
            .order_by(PayrollLineItemModel.employee_name.asc())
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def get_line_item_by_id(self, line_item_id: UUID) -> PayrollLineItem | None:
        """Fetch a single line item by id."""
        result = await self.session.get(PayrollLineItemModel, line_item_id)
        return result.to_domain() if result else None

    async def update_line_items(self, line_items: Sequence[PayrollLineItem]) -> None:
        """Update existing line items (e.g. mark paid)."""
        for item in line_items:
            await self.session.merge(PayrollLineItemModel.from_domain(item))
        await self.session.flush()

    async def list_warnings(self, run_id: UUID) -> Sequence[PayrollWarning]:
        """List all warnings attached to a run's line items.

        Warnings are keyed on ``payroll_line_item_id``; we join through
        ``payroll_line_items`` filtered by ``payroll_run_id`` to gather every
        warning belonging to the run.
        """
        result = await self.session.execute(
            select(PayrollWarningModel)
            .join(
                PayrollLineItemModel,
                PayrollLineItemModel.id == PayrollWarningModel.payroll_line_item_id,
            )
            .where(PayrollLineItemModel.payroll_run_id == run_id)
            .order_by(PayrollWarningModel.created_at.asc())
        )
        return [model.to_domain() for model in result.scalars().all()]
