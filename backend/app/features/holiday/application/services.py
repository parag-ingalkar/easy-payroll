from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.features.holiday.application.ports import HolidaysRepositoryPort
from app.features.holiday.domain.entities import Holiday
from app.features.holiday.domain.exceptions import HolidayNotFoundError


@dataclass
class HolidayService:
    """Application service — the sole gateway to ``HolidaysRepositoryPort``.

    Own-feature use cases depend on this concrete class.
    """

    holiday_repo: HolidaysRepositoryPort

    async def get_or_raise(self, business_id: UUID, holiday_date: date) -> Holiday:
        """Fetch a holiday, raising ``HolidayNotFoundError`` if absent."""
        holiday = await self.holiday_repo.get_by_business_id_and_date(business_id, holiday_date)
        if not holiday:
            raise HolidayNotFoundError(business_id, holiday_date)
        return holiday

    async def get_by_business_and_date(
        self, business_id: UUID, holiday_date: date
    ) -> Holiday | None:
        return await self.holiday_repo.get_by_business_id_and_date(business_id, holiday_date)

    async def add(self, holiday: Holiday) -> None:
        await self.holiday_repo.add(holiday)

    async def delete(self, holiday: Holiday) -> None:
        await self.holiday_repo.delete(holiday)

    async def list_by_business(
        self,
        business_id: UUID,
        year: int | None = None,
        month: int | None = None,
    ) -> Sequence[Holiday]:
        return await self.holiday_repo.list_by_business(business_id, year=year, month=month)
