from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.business.domain.value_objects import DivisorPolicy, WeekDay


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
    divisor_policy: DivisorPolicy
    default_overtime_multiplier: Decimal
    default_weekly_off_days: list[WeekDay]
    default_working_hours: Decimal
    created_at: datetime
