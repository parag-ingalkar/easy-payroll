"""SQLAlchemy ORM model for the transaction domain."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.features.transaction.domain.entities import Transaction
from app.features.transaction.domain.value_objects import TransactionType

transaction_type_enum = SAEnum(
    TransactionType,
    name="transaction_type_enum",
    values_callable=lambda x: [e.value for e in x],
)


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[TransactionType] = mapped_column(transaction_type_enum, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    @classmethod
    def from_domain(cls, transaction: "Transaction") -> "TransactionModel":
        return cls(
            id=transaction.id,
            employee_id=transaction.employee_id,
            transaction_date=transaction.transaction_date,
            type=transaction.type,
            amount=transaction.amount,
            description=transaction.description,
            created_at=transaction.created_at,
        )

    def to_domain(self) -> "Transaction":
        return Transaction(
            id=self.id,
            employee_id=self.employee_id,
            transaction_date=self.transaction_date,
            type=self.type,
            amount=self.amount,
            description=self.description,
            created_at=self.created_at,
        )
