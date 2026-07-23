from typing import Protocol
from uuid import UUID

from app.features.business.domain.entities import Business
from app.features.employee.domain.entities import Employee
from app.features.transaction.domain.entities import Transaction


class TransactionRepositoryPort(Protocol):
    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Fetches a transaction by its ID."""
        ...

    async def get_all_by_employee_id(self, employee_id: UUID) -> list[Transaction]:
        """Fetches all transactions for a given employee ID."""
        ...

    async def add(self, transaction: Transaction) -> None:
        """Adds a new transaction to the repository."""
        ...

    async def update(self, transaction: Transaction) -> None:
        """Updates an existing transaction in the repository."""
        ...

    async def delete(self, transaction: Transaction) -> None:
        """Deletes a transaction from the repository."""
        ...


class BusinessServicePort(Protocol):
    """Cross-feature port for the transaction feature to access business capability.

    Satisfied structurally by ``BusinessService`` (business feature). Defined
    here — the consumer — per hexagonal/ports-and-adapters convention.
    """

    async def get_owned_business(self, business_id: UUID, owner_id: UUID) -> Business:
        """Fetch a business and verify it is owned by ``owner_id``."""
        ...


class EmployeeServicePort(Protocol):
    """Cross-feature port for the transaction feature to access employee capability.

    Satisfied structurally by ``EmployeeService`` (employee feature). Defined
    here — the consumer — per hexagonal/ports-and-adapters convention.
    """

    async def get_owned_employee(
        self, employee_id: UUID, business_id: UUID
    ) -> Employee:
        """Fetch an employee and verify it belongs to the given business."""
        ...
