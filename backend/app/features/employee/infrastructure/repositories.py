from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.employee.application.ports import EmployeeRepositoryPort
from app.features.employee.domain.entities import Employee
from app.features.employee.infrastructure.models import EmployeeModel


class SQLEmployeeRepository(EmployeeRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_business_id_and_name(self, business_id: UUID, name: str) -> Employee | None:
        """Fetches an employee by business ID and name."""
        result = await self.session.execute(
            select(EmployeeModel).where(
                EmployeeModel.business_id == business_id, EmployeeModel.name == name
            )
        )
        employee_model = result.scalar_one_or_none()
        return employee_model.to_domain() if employee_model else None

    async def get_by_id(self, employee_id: UUID) -> Employee | None:
        """Fetches an employee by its ID."""
        result = await self.session.get(EmployeeModel, employee_id)
        return result.to_domain() if result else None

    async def add(self, employee: Employee) -> None:
        """Adds a new employee to the repository."""
        employee_model = EmployeeModel.from_domain(employee)
        self.session.add(employee_model)
        await self.session.flush()  # Ensure the employee is persisted and ID is generated

    async def update(self, employee: Employee) -> None:
        """Updates an existing employee in the repository."""
        model = EmployeeModel.from_domain(employee)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, employee: Employee) -> None:
        """Deletes an employee from the repository."""
        model = await self.session.get(EmployeeModel, employee.id)
        if model is None:
            return
        await self.session.delete(model)

    async def get_all_by_business_id(
        self, business_id: UUID, include_inactive: bool
    ) -> list[Employee]:
        """Fetches all employees for a given business ID."""
        query = select(EmployeeModel).where(EmployeeModel.business_id == business_id)
        if not include_inactive:
            query = query.where(EmployeeModel.is_active)

        result = await self.session.execute(query)
        employees_models = result.scalars().all()
        return [employee_model.to_domain() for employee_model in employees_models]
