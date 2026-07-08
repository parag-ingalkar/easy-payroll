from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.holiday.application.ports import HolidaysRepositoryPort
from app.features.holiday.domain.entities import Holiday
from app.features.holiday.infrastructure.models import HolidayModel


class SQLHolidaysRepository(HolidaysRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, holiday: Holiday) -> None:
        """Add a new holiday to the repository."""
        holiday_model = HolidayModel.from_entity(holiday)
        self.session.add(holiday_model)
        await self.session.flush()  # Ensure the holiday is persisted and ID is generated

    async def get_by_business_id_and_date(
        self, business_id: UUID, holiday_date: date
    ) -> Holiday | None:
        """Retrieve a holiday by business ID and date."""
        result = await self.session.execute(
            select(HolidayModel).where(
                HolidayModel.business_id == business_id,
                HolidayModel.holiday_date == holiday_date,
            )
        )
        holiday_model = result.scalar_one_or_none()
        return holiday_model.to_entity() if holiday_model else None

    async def list_by_business(
        self, business_id: UUID, year: int | None = None, month: int | None = None
    ) -> Sequence[Holiday]:
        """List holidays for a business, optionally filtered by year and month."""
        query = select(HolidayModel).where(HolidayModel.business_id == business_id)

        if year is not None:
            query = query.where(extract("year", HolidayModel.holiday_date) == year)
        if month is not None:
            query = query.where(extract("month", HolidayModel.holiday_date) == month)

        result = await self.session.execute(query)
        holiday_models = result.scalars().all()
        return [holiday_model.to_entity() for holiday_model in holiday_models]

    async def delete(self, holiday: Holiday) -> None:
        """Delete a holiday."""
        holiday_model = await self.session.get(HolidayModel, holiday.id)
        if holiday_model is None:
            return
        await self.session.delete(holiday_model)
        await self.session.flush()
