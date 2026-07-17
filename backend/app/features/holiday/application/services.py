from uuid import UUID
from datetime import date
from app.features.holiday.application.ports import HolidaysRepositoryPort
from app.features.holiday.domain.entities import Holiday
from app.features.holiday.domain.exceptions import HolidayNotFoundError


async def get_existing_holiday(
    holiday_repo: HolidaysRepositoryPort, business_id: UUID, holiday_date: date
) -> Holiday:
    holiday = await holiday_repo.get_by_business_id_and_date(business_id, holiday_date)
    if not holiday:
        raise HolidayNotFoundError(business_id, holiday_date)
    return holiday
