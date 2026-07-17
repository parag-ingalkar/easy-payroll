from typing import Protocol
from uuid import UUID

from app.features.employee.domain.entities import Employee


class EmployeeRepositoryPort(Protocol):
    async def get_by_business_id_and_name(self, business_id: UUID, name: str) -> Employee | None:
        """Fetches an employee by business ID and name."""
        ...

    async def get_by_id(self, employee_id: UUID) -> Employee | None:
        """Fetches an employee by its ID."""
        ...

    async def add(self, employee: Employee) -> None:
        """Adds a new employee to the repository."""
        ...

    async def update(self, employee: Employee) -> None:
        """Updates an existing employee in the repository."""
        ...

    async def delete(self, employee: Employee) -> None:
        """Deletes an employee from the repository."""
        ...

    async def get_all_by_business_id(
        self, business_id: UUID, include_inactive: bool
    ) -> list[Employee]:
        """Fetches all employees for a given business ID."""
        ...
