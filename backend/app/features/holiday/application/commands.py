from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.features.holiday.domain.value_objects import HolidayType


@dataclass(frozen=True)
class CreateHolidayCommand:
    business_id: UUID
    owner_id: UUID
    holiday_date: date
    name: str
    holiday_type: HolidayType
    is_paid: bool


@dataclass(frozen=True)
class DeleteHolidayCommand:
    business_id: UUID
    owner_id: UUID
    holiday_date: date


@dataclass(frozen=True)
class GetHolidayCommand:
    business_id: UUID
    owner_id: UUID
    holiday_date: date


@dataclass(frozen=True)
class ListHolidaysCommand:
    business_id: UUID
    owner_id: UUID
    year: int | None = None
    month: int | None = None
