
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.business.infrastructure.repositories import SQLBusinessRepository
from app.features.employee.application.use_cases import (
    ActivateEmployeeUseCase,
    CreateEmployeeUseCase,
    DeactivateEmployeeUseCase,
    DeleteEmployeeUseCase,
    GetEmployeesUseCase,
    GetEmployeeUseCase,
    UpdateEmployeeUseCase,
)
from app.features.employee.infrastructure.repositories import SQLEmployeeRepository


def get_create_employee_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return CreateEmployeeUseCase(uow=uow, employee_repo=employee_repo, business_repo=business_repo)


def get_update_employee_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return UpdateEmployeeUseCase(uow=uow, employee_repo=employee_repo, business_repo=business_repo)


def get_delete_employee_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return DeleteEmployeeUseCase(uow=uow, employee_repo=employee_repo, business_repo=business_repo)


def get_get_employee_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return GetEmployeeUseCase(employee_repo=employee_repo, business_repo=business_repo)


def get_get_employees_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return GetEmployeesUseCase(employee_repo=employee_repo, business_repo=business_repo)


def get_activate_employee_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return ActivateEmployeeUseCase(uow=uow, employee_repo=employee_repo, business_repo=business_repo)


def get_deactivate_employee_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    employee_repo = SQLEmployeeRepository(db_session)
    business_repo = SQLBusinessRepository(db_session)
    return DeactivateEmployeeUseCase(uow=uow, employee_repo=employee_repo, business_repo=business_repo)