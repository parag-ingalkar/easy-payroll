from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from app.features.holiday.domain.value_objects import HolidayType


@dataclass
class Holiday:
    """A single date marked as a holiday for a business.

    Paid holidays count as full paid days in salary calculation and are
    auto-derived in the attendance read-model (PRODUCT.md → Attendance States).
    Stored under the business domain (ADR-022).
    """

    id: UUID
    business_id: UUID
    holiday_date: date
    name: str
    holiday_type: HolidayType
    is_paid: bool

    @classmethod
    def create(
        cls,
        *,
        business_id: UUID,
        holiday_date: date,
        name: str,
        holiday_type: HolidayType,
        is_paid: bool,
    ) -> "Holiday":
        """Factory method for creating a new holiday entity."""
        return cls(
            id=uuid4(),
            business_id=business_id,
            holiday_date=holiday_date,
            name=name,
            holiday_type=holiday_type,
            is_paid=is_paid,
        )
