from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.features.business.domain.entities import Business
from app.features.business.domain.value_objects import DivisorPolicy, WeekDay

divisor_policy_type = SAEnum(
    DivisorPolicy,
    name="divisor_policy_enum",
    values_callable=lambda x: [e.value for e in x],
)

weekday_type = SAEnum(
    WeekDay,
    name="weekday_enum",
    values_callable=lambda x: [e.value for e in x],
)


class BusinessModel(Base):
    __tablename__ = "businesses"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    divisor_policy: Mapped[DivisorPolicy] = mapped_column(divisor_policy_type, nullable=False)
    default_overtime_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(precision=3, scale=1), nullable=False, default=Decimal("2.0")
    )
    default_weekly_off_days: Mapped[list[WeekDay]] = mapped_column(
        ARRAY(weekday_type), nullable=False, default=[WeekDay.SUNDAY]
    )
    default_working_hours: Mapped[Decimal] = mapped_column(
        Numeric(precision=3, scale=2), nullable=False, default=Decimal("8.0")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint("owner_id", "slug", name="uq_business_owner_slug"),)

    @classmethod
    def from_domain(cls, business: Business) -> "BusinessModel":
        return cls(
            id=business.id,
            owner_id=business.owner_id,
            name=business.name,
            slug=business.slug,
            divisor_policy=business.divisor_policy,
            default_overtime_multiplier=business.default_overtime_multiplier,
            default_weekly_off_days=business.default_weekly_off_days,
            default_working_hours=business.default_working_hours,
            created_at=business.created_at,
        )

    def to_domain(self) -> Business:
        return Business(
            id=self.id,
            owner_id=self.owner_id,
            name=self.name,
            slug=self.slug,
            divisor_policy=self.divisor_policy,
            default_overtime_multiplier=self.default_overtime_multiplier,
            default_weekly_off_days=self.default_weekly_off_days,
            default_working_hours=self.default_working_hours,
            created_at=self.created_at,
        )
