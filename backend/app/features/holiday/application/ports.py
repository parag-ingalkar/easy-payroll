from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import UUID

from app.features.business.domain.entities import Business
from app.features.holiday.domain.entities import Holiday


class HolidaysRepositoryPort(Protocol):
    """Protocol for the holidays repository."""

    async def add(self, holiday: Holiday) -> None:
        """Add a new holiday to the repository."""
        ...

    async def get_by_business_id_and_date(
        self, business_id: UUID, holiday_date: date
    ) -> Holiday | None:
        """Retrieve a holiday by business ID and date."""
        ...

    async def list_by_business(
        self, business_id: UUID, year: int | None = None, month: int | None = None
    ) -> Sequence[Holiday]:
        """List holidays for a business, optionally filtered by year and month."""
        ...

    async def delete(self, holiday: Holiday) -> None:
        """Delete a holiday."""
        ...


class BusinessServicePort(Protocol):
    """Cross-feature port for the holiday feature to access business capability.

    Satisfied structurally by ``BusinessService`` (business feature). Defined
    here — the consumer — per hexagonal/ports-and-adapters convention.
    """

    async def get_owned_business(self, business_id: UUID, owner_id: UUID) -> Business:
        """Fetch a business and verify it is owned by ``owner_id``."""
        ...
