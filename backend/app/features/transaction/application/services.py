from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.features.employee.domain.entities import Employee
from app.features.transaction.application.ports import TransactionRepositoryPort
from app.features.transaction.domain.entities import Transaction
from app.features.transaction.domain.exceptions import TransactionNotFoundError


@dataclass
class TransactionService:
    """Application service — the sole gateway to ``TransactionRepositoryPort``.

    Own-feature use cases depend on this concrete class.
    """

    transaction_repo: TransactionRepositoryPort

    async def get_or_raise(self, transaction_id: UUID) -> Transaction:
        """Fetch a transaction, raising ``TransactionNotFoundError`` if absent."""
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise TransactionNotFoundError(transaction_id=transaction_id)
        return transaction

    async def get_owned_transaction(self, transaction_id: UUID, employee: Employee) -> Transaction:
        """Fetch a transaction and verify it belongs to the given employee.

        Raises ``TransactionNotFoundError`` if the transaction does not exist,
        and ``TransactionNotOwnedError`` (via the entity invariant) if it exists
        but belongs to a different employee.
        """
        transaction = await self.get_or_raise(transaction_id)
        transaction.ensure_belongs_to_employee(employee.id)
        return transaction

    async def get_all_by_employee_id(self, employee_id: UUID) -> list[Transaction]:
        return await self.transaction_repo.get_all_by_employee_id(employee_id)

    async def get_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[Transaction]:
        return await self.transaction_repo.get_by_employee_and_date_range(
            employee_id, start_date, end_date
        )

    async def add(self, transaction: Transaction) -> None:
        await self.transaction_repo.add(transaction)

    async def update(self, transaction: Transaction) -> None:
        await self.transaction_repo.update(transaction)

    async def delete(self, transaction: Transaction) -> None:
        await self.transaction_repo.delete(transaction)
