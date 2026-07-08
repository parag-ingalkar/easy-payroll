from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.features.holiday.domain.entities import Holiday
from app.features.holiday.domain.value_objects import HolidayType


class HolidayModel(Base):
    __tablename__ = "holidays"
    __table_args__ = (UniqueConstraint("business_id", "holiday_date", name="uq_holidays_biz_date"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    holiday_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    holiday_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default="custom", server_default="custom"
    )
    is_paid: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    @classmethod
    def from_entity(cls, holiday_entity: "Holiday") -> "HolidayModel":
        """Create a HolidayModel instance from a Holiday entity."""
        return cls(
            id=holiday_entity.id,
            business_id=holiday_entity.business_id,
            holiday_date=holiday_entity.holiday_date,
            name=holiday_entity.name,
            holiday_type=holiday_entity.holiday_type.value,
            is_paid=holiday_entity.is_paid,
        )

    def to_entity(self) -> "Holiday":
        """Convert the HolidayModel instance to a Holiday entity."""

        return Holiday(
            id=self.id,
            business_id=self.business_id,
            holiday_date=self.holiday_date,
            name=self.name,
            holiday_type=HolidayType(self.holiday_type),
            is_paid=self.is_paid,
        )
