"""Business-domain command objects."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from ..domain.value_objects import DivisorPolicy, WeekDay


@dataclass(frozen=True)
class CreateBusinessCommand:
    owner_id: UUID
    name: str
    divisor_policy: DivisorPolicy
    default_overtime_multiplier: Decimal | None
    default_weekly_off_days: Sequence[WeekDay] | None
    default_working_hours: Decimal | None


@dataclass(frozen=True)
class UpdateBusinessCommand:
    business_id: UUID
    owner_id: UUID
    name: str | None = None
    divisor_policy: DivisorPolicy | None = None
    default_overtime_multiplier: Decimal | None = None
    default_weekly_off_days: Sequence[WeekDay] | None = None
    default_working_hours: Decimal | None = None


@dataclass(frozen=True)
class DeleteBusinessCommand:
    business_id: UUID
    owner_id: UUID
