from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.transaction.application.ports import TransactionRepositoryPort
from app.features.transaction.domain.entities import Transaction
from app.features.transaction.infrastructure.models import TransactionModel


class SQLTransactionRepository(TransactionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Fetches a transaction by its ID."""
        result = await self.session.get(TransactionModel, transaction_id)
        return result.to_domain() if result else None

    async def get_all_by_employee_id(self, employee_id: UUID) -> list[Transaction]:
        """Fetches all transactions for a given employee ID."""
        result = await self.session.execute(
            select(TransactionModel)
            .where(TransactionModel.employee_id == employee_id)
            .order_by(TransactionModel.transaction_date.desc())
        )
        transaction_models = result.scalars().all()
        return [transaction_model.to_domain() for transaction_model in transaction_models]

    async def add(self, transaction: Transaction) -> None:
        """Adds a new transaction to the repository."""
        transaction_model = TransactionModel.from_domain(transaction)
        self.session.add(transaction_model)
        await self.session.flush()  # Ensure the transaction is persisted and ID is generated

    async def update(self, transaction: Transaction) -> None:
        """Updates an existing transaction in the repository."""
        model = TransactionModel.from_domain(transaction)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, transaction: Transaction) -> None:
        """Deletes a transaction from the repository."""
        model = await self.session.get(TransactionModel, transaction.id)
        if model is None:
            return
        await self.session.delete(model)
