from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.features.auth.domain.entities import CurrentUser
from app.features.auth.presentation.dependencies import get_current_user
from app.features.employee.application.commands import (
    ActivateEmployeeCommand,
    CreateEmployeeCommand,
    DeactivateEmployeeCommand,
    DeleteEmployeeCommand,
    GetEmployeeCommand,
    GetEmployeesCommand,
    UpdateEmployeeCommand,
)
from app.features.employee.application.use_cases import (
    ActivateEmployeeUseCase,
    CreateEmployeeUseCase,
    DeactivateEmployeeUseCase,
    DeleteEmployeeUseCase,
    GetEmployeesUseCase,
    GetEmployeeUseCase,
    UpdateEmployeeUseCase,
)
from app.features.employee.presentation.dependencies import (
    get_activate_employee_use_case,
    get_create_employee_use_case,
    get_deactivate_employee_use_case,
    get_delete_employee_use_case,
    get_get_employee_use_case,
    get_get_employees_use_case,
    get_update_employee_use_case,
)
from app.features.employee.presentation.schemas import (
    CreateEmployeeRequest,
    EmployeeResponse,
    UpdateEmployeeRequest,
)

router = APIRouter()


@router.post(
    "/business/{business_id}/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    business_id: UUID,
    body: CreateEmployeeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: CreateEmployeeUseCase = Depends(get_create_employee_use_case),
) -> EmployeeResponse:
    command = CreateEmployeeCommand(
        business_id=business_id,
        current_user=current_user,
        name=body.name,
        phone=body.phone,
        designation=body.designation,
        salary_type=body.salary_type,
        base_rate=body.base_rate,
        overtime_multiplier=body.overtime_multiplier,
        weekly_off_days=body.weekly_off_days,
        working_hours=body.working_hours,
        joining_date=body.joining_date,
    )
    employee = await use_case.execute(command)
    return EmployeeResponse.model_validate(employee)


@router.get("/business/{business_id}/employees", response_model=list[EmployeeResponse])
async def get_employees(
    business_id: UUID,
    include_inactive: Annotated[
        bool, Query(description="Filter to include inactive staff")
    ] = False,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: GetEmployeesUseCase = Depends(get_get_employees_use_case),
) -> list[EmployeeResponse]:
    command = GetEmployeesCommand(
        business_id=business_id,
        current_user=current_user,
        include_inactive=include_inactive,
    )
    employees = await use_case.execute(command)
    return [EmployeeResponse.model_validate(employee) for employee in employees]


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: GetEmployeeUseCase = Depends(get_get_employee_use_case),
) -> EmployeeResponse:
    command = GetEmployeeCommand(
        employee_id=employee_id,
        current_user=current_user,
    )
    employee = await use_case.execute(command)
    return EmployeeResponse.model_validate(employee)


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    body: UpdateEmployeeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: UpdateEmployeeUseCase = Depends(get_update_employee_use_case),
) -> EmployeeResponse:
    command = UpdateEmployeeCommand(
        employee_id=employee_id,
        current_user=current_user,
        name=body.name,
        phone=body.phone,
        designation=body.designation,
        salary_type=body.salary_type,
        base_rate=body.base_rate,
        overtime_multiplier=body.overtime_multiplier,
        weekly_off_days=body.weekly_off_days,
        working_hours=body.working_hours,
        joining_date=body.joining_date,
    )
    employee = await use_case.execute(command)
    return EmployeeResponse.model_validate(employee)


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: DeleteEmployeeUseCase = Depends(get_delete_employee_use_case),
) -> None:
    command = DeleteEmployeeCommand(
        employee_id=employee_id,
        current_user=current_user,
    )
    await use_case.execute(command)


@router.patch("/employees/{employee_id}/activate", response_model=EmployeeResponse)
async def activate_employee(
    employee_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: ActivateEmployeeUseCase = Depends(get_activate_employee_use_case),
) -> EmployeeResponse:
    command = ActivateEmployeeCommand(
        employee_id=employee_id,
        current_user=current_user,
    )
    employee = await use_case.execute(command)
    return EmployeeResponse.model_validate(employee)


@router.patch("/employees/{employee_id}/deactivate", response_model=EmployeeResponse)
async def deactivate_employee(
    employee_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: DeactivateEmployeeUseCase = Depends(get_deactivate_employee_use_case),
) -> EmployeeResponse:
    command = DeactivateEmployeeCommand(
        employee_id=employee_id,
        current_user=current_user,
    )
    employee = await use_case.execute(command)
    return EmployeeResponse.model_validate(employee)
