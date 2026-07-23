"""Pydantic request/response schemas for the transaction API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.transaction.domain.value_objects import TransactionType


class CreateTransactionRequest(BaseModel):
    transaction_date: date
    type: TransactionType
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    description: str = Field(..., min_length=1, max_length=255)


class UpdateTransactionRequest(BaseModel):
    """Every field optional — PATCH semantics. Only provided fields are applied."""

    transaction_date: date | None = None
    type: TransactionType | None = None
    amount: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    description: str | None = Field(default=None, min_length=1, max_length=255)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    transaction_date: date
    type: TransactionType
    amount: Decimal
    description: str
    created_at: datetime
