from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.features.auth.domain.entities import CurrentUser
from app.features.transaction.domain.value_objects import TransactionType


@dataclass(frozen=True)
class CreateTransactionCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    transaction_date: date
    type: TransactionType
    amount: Decimal
    description: str


@dataclass(frozen=True)
class UpdateTransactionCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    transaction_id: UUID
    transaction_date: date | None = None
    type: TransactionType | None = None
    amount: Decimal | None = None
    description: str | None = None


@dataclass(frozen=True)
class GetTransactionsCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID


@dataclass(frozen=True)
class GetTransactionCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    transaction_id: UUID


@dataclass(frozen=True)
class DeleteTransactionCommand:
    current_user: CurrentUser
    business_id: UUID
    employee_id: UUID
    transaction_id: UUID
