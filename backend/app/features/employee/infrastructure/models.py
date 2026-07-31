"""SQLAlchemy ORM model for the employee domain."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.features.business.infrastructure.models import weekday_type
from app.features.employee.domain.entities import Employee
from app.features.employee.domain.value_objects import SalaryType
from app.shared.enums import WeekDay

salary_type_enum = SAEnum(
    SalaryType,
    name="salary_type_enum",
    values_callable=lambda x: [e.value for e in x],
)


class EmployeeModel(Base):
    __tablename__ = "employees"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary_type: Mapped[SalaryType] = mapped_column(salary_type_enum, nullable=False)
    base_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    overtime_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, default=Decimal("2.0"), server_default="2.0"
    )
    weekly_off_days: Mapped[list[WeekDay]] = mapped_column(
        ARRAY(weekday_type), nullable=False, default=[WeekDay.SUNDAY]
    )
    working_hours: Mapped[Decimal] = mapped_column(
        Numeric(precision=4, scale=2), nullable=False, default=Decimal("8.0")
    )
    joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("business_id", "name", name="uq_employee_business_name"),)

    @classmethod
    def from_domain(cls, employee: "Employee") -> "EmployeeModel":
        return cls(
            id=employee.id,
            business_id=employee.business_id,
            name=employee.name,
            phone=employee.phone,
            designation=employee.designation,
            salary_type=employee.salary_type,
            base_rate=employee.base_rate,
            overtime_multiplier=employee.overtime_multiplier,
            weekly_off_days=employee.weekly_off_days,
            working_hours=employee.working_hours,
            joining_date=employee.joining_date,
            is_active=employee.is_active,
            created_at=employee.created_at,
        )

    def to_domain(self) -> "Employee":
        return Employee(
            id=self.id,
            business_id=self.business_id,
            name=self.name,
            phone=self.phone,
            designation=self.designation,
            salary_type=self.salary_type,
            base_rate=self.base_rate,
            overtime_multiplier=self.overtime_multiplier,
            weekly_off_days=self.weekly_off_days,
            working_hours=self.working_hours,
            joining_date=self.joining_date,
            is_active=self.is_active,
            created_at=self.created_at,
        )
