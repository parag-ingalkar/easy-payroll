from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.holiday.domain.value_objects import HolidayType


class HolidayBase(BaseModel):
    holiday_date: date
    name: str = Field(min_length=1, max_length=120)
    holiday_type: HolidayType = Field(default=HolidayType.CUSTOM)
    is_paid: bool = Field(default=True)


class CreateHolidayRequest(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    id: UUID
    business_id: UUID

    model_config = ConfigDict(from_attributes=True)
