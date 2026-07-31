"""Transaction-domain entities — pure Python dataclasses."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.features.transaction.domain.exceptions import (
    InvalidTransactionAmountError,
    TransactionNotOwnedError,
)
from app.features.transaction.domain.value_objects import TransactionType


@dataclass
class Transaction:
    """A single deduction or addition of an amount against an employee.

    ``amount`` is always strictly positive; the direction of the effect on
    payroll is encoded by ``type`` (ADDITION / DEDUCTION), never by the sign
    of ``amount``. The ``amount > 0`` invariant is owned by this entity and is
    enforced in :meth:`create` and :meth:`update`.
    """

    id: UUID
    employee_id: UUID
    transaction_date: date
    type: TransactionType
    amount: Decimal
    description: str
    created_at: datetime

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidTransactionAmountError(amount=amount)

    @classmethod
    def create(
        cls,
        *,
        employee_id: UUID,
        transaction_date: date,
        type: TransactionType,
        amount: Decimal,
        description: str,
    ) -> "Transaction":
        """Factory method for creating a new transaction entity."""
        cls._validate_amount(amount)
        return cls(
            id=uuid4(),
            employee_id=employee_id,
            transaction_date=transaction_date,
            type=type,
            amount=amount,
            description=description,
            created_at=datetime.now(),
        )

    def update(
        self,
        *,
        transaction_date: date | None = None,
        type: TransactionType | None = None,
        amount: Decimal | None = None,
        description: str | None = None,
    ) -> None:
        """Update the transaction with the given keyword arguments (PATCH semantics)."""
        if transaction_date is not None:
            self.transaction_date = transaction_date
        if type is not None:
            self.type = type
        if amount is not None:
            self._validate_amount(amount)
            self.amount = amount
        if description is not None:
            self.description = description

    def ensure_belongs_to_employee(self, employee_id: UUID) -> None:
        """Ensure that the transaction belongs to the given employee."""
        if self.employee_id != employee_id:
            raise TransactionNotOwnedError(transaction_id=self.id, employee_id=employee_id)
