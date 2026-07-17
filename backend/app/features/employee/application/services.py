from uuid import UUID

from app.features.business.domain.entities import Business
from app.features.employee.application.ports import EmployeeRepositoryPort
from app.features.employee.domain.entities import Employee
from app.features.employee.domain.exceptions import (
    EmployeeNotFoundError,
)


async def get_owned_employee(
    employee_repo: EmployeeRepositoryPort,
    employee_id: UUID,
    business: Business,
) -> Employee:
    """Fetch an employee and verify it belongs to the given (already-owned) business.

    Raises EmployeeNotFoundError if the employee does not exist, and
    EmployeeNotOwnedError if it exists but belongs to a different business.
    """
    employee = await employee_repo.get_by_id(employee_id)
    if not employee:
        raise EmployeeNotFoundError(employee_id=employee_id)
    employee.ensure_belongs_to_business(business.id)
    return employee
