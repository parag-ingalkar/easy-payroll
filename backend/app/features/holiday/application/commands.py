from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.features.auth.domain.entities import CurrentUser
from app.features.holiday.domain.value_objects import HolidayType


@dataclass(frozen=True)
class CreateHolidayCommand:
    current_user: CurrentUser
    business_id: UUID
    holiday_date: date
    name: str
    holiday_type: HolidayType
    is_paid: bool


@dataclass(frozen=True)
class DeleteHolidayCommand:
    current_user: CurrentUser
    business_id: UUID
    holiday_date: date


@dataclass(frozen=True)
class GetHolidayCommand:
    current_user: CurrentUser
    business_id: UUID
    holiday_date: date


@dataclass(frozen=True)
class ListHolidaysCommand:
    current_user: CurrentUser
    business_id: UUID
    year: int | None = None
    month: int | None = None
