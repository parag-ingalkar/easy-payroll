from dataclasses import dataclass
from uuid import UUID

from app.features.employee.application.ports import EmployeeRepositoryPort
from app.features.employee.domain.entities import Employee
from app.features.employee.domain.exceptions import (
    EmployeeNotFoundError,
)


@dataclass
class EmployeeService:
    """Application service — the sole gateway to ``EmployeeRepositoryPort``.

    Own-feature use cases depend on this concrete class. Cross-feature
    consumers declare their own narrow ``Protocol`` port (e.g.
    ``EmployeeServicePort`` in the transaction feature) which this class
    satisfies structurally.
    """

    employee_repo: EmployeeRepositoryPort

    async def get_by_id_or_raise(self, employee_id: UUID) -> Employee:
        """Fetch an employee by id, raising ``EmployeeNotFoundError`` if absent."""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundError(employee_id=employee_id)
        return employee

    async def get_owned_employee(
        self, employee_id: UUID, business_id: UUID
    ) -> Employee:
        """Fetch an employee and verify it belongs to the given business.

        Raises ``EmployeeNotFoundError`` if the employee does not exist, and
        ``EmployeeNotOwnedError`` (via the entity invariant) if it exists but
        belongs to a different business.
        """
        employee = await self.get_by_id_or_raise(employee_id)
        employee.ensure_belongs_to_business(business_id)
        return employee

    async def get_by_business_and_name(
        self, business_id: UUID, name: str
    ) -> Employee | None:
        return await self.employee_repo.get_by_business_id_and_name(business_id, name)

    async def add(self, employee: Employee) -> None:
        await self.employee_repo.add(employee)

    async def update(self, employee: Employee) -> None:
        await self.employee_repo.update(employee)

    async def delete(self, employee: Employee) -> None:
        await self.employee_repo.delete(employee)

    async def list_by_business(
        self, business_id: UUID, include_inactive: bool = False
    ) -> list[Employee]:
        return await self.employee_repo.get_all_by_business_id(
            business_id, include_inactive=include_inactive
        )
