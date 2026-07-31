from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.features.business.domain.value_objects import DivisorPolicy
from app.shared.enums import WeekDay


def _serialize_decimal(value: Decimal) -> float:
    """Convert Decimal to float for JSON serialization."""
    return float(value)


class CreateBusinessRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    divisor_policy: DivisorPolicy
    default_overtime_multiplier: Decimal | None = Field(
        default=None, max_digits=3, decimal_places=1
    )
    default_weekly_off_days: list[WeekDay] | None = None
    default_working_hours: Decimal | None = Field(default=None, ge=1, le=24)


class UpdateBusinessRequest(BaseModel):
    """Every field optional — PATCH semantics. Only provided fields are applied."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    divisor_policy: DivisorPolicy | None = None
    default_overtime_multiplier: Decimal | None = Field(
        default=None, max_digits=3, decimal_places=1
    )
    default_weekly_off_days: list[WeekDay] | None = None
    default_working_hours: Decimal | None = Field(default=None, ge=1, le=24)


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    slug: str
    divisor_policy: DivisorPolicy
    default_overtime_multiplier: Decimal
    default_weekly_off_days: list[WeekDay]
    default_working_hours: Decimal
    created_at: datetime

    @field_serializer("default_overtime_multiplier", "default_working_hours")
    def serialize_decimals(self, value: Decimal) -> float:
        return _serialize_decimal(value)
