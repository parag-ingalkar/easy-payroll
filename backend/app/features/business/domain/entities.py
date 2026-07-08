"""Business-domain entities — pure Python dataclasses."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from .value_objects import DivisorPolicy, WeekDay


@dataclass
class Business:
    """A business owned by a registered user.

    The default fields (``default_overtime_multiplier``,
    ``default_weekly_off_days``, ``default_working_hours``) are copied onto each
    new employee at creation time (ADR-015/ADR-018) — they are NOT resolved at
    runtime during payroll.
    """

    id: UUID
    owner_id: UUID
    name: str
    slug: str
    divisor_policy: DivisorPolicy
    default_overtime_multiplier: Decimal
    default_weekly_off_days: Sequence[WeekDay]
    default_working_hours: Decimal
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        owner_id: UUID,
        name: str,
        divisor_policy: DivisorPolicy,
        default_overtime_multiplier: Decimal | None,
        default_weekly_off_days: Sequence[WeekDay] | None,
        default_working_hours: Decimal | None,
    ) -> "Business":
        """Factory method for creating a new business entity."""
        slug = name.lower().replace(" ", "-")
        return cls(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            slug=slug,
            divisor_policy=divisor_policy,
            default_overtime_multiplier=default_overtime_multiplier or Decimal("2.0"),
            default_weekly_off_days=default_weekly_off_days or [WeekDay.SUNDAY],
            default_working_hours=default_working_hours or Decimal("8.0"),
            created_at=datetime.now(UTC),
        )

    def update(self, **kwargs) -> None:
        """Update the business entity with the given keyword arguments."""
        if "name" in kwargs:
            self.name = kwargs["name"]
            self.slug = kwargs["name"].lower().replace(" ", "-")
        if "divisor_policy" in kwargs:
            self.divisor_policy = kwargs["divisor_policy"]
        if "default_overtime_multiplier" in kwargs:
            self.default_overtime_multiplier = kwargs["default_overtime_multiplier"]
        if "default_weekly_off_days" in kwargs:
            self.default_weekly_off_days = kwargs["default_weekly_off_days"]
        if "default_working_hours" in kwargs:
            self.default_working_hours = kwargs["default_working_hours"]
