from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.application.services import get_owned_business
from app.features.employee.application.commands import (
    ActivateEmployeeCommand,
    CreateEmployeeCommand,
    DeactivateEmployeeCommand,
    DeleteEmployeeCommand,
    GetEmployeeCommand,
    GetEmployeesCommand,
    UpdateEmployeeCommand,
)
from app.features.employee.application.ports import EmployeeRepositoryPort
from app.features.employee.application.services import get_owned_employee
from app.features.employee.domain.entities import Employee
from app.features.employee.domain.exceptions import (
    EmployeeAlreadyExistsError,
)


@dataclass
class CreateEmployeeUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: CreateEmployeeCommand) -> Employee:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.current_user_id
            )

            existing_employee = await self.employee_repo.get_by_business_id_and_name(
                business.id, command.name
            )
            if existing_employee:
                raise EmployeeAlreadyExistsError(business_id=business.id, name=command.name)

            overtime_multiplier = (
                command.overtime_multiplier
                if command.overtime_multiplier
                else business.default_overtime_multiplier
            )
            weekly_off_days = (
                command.weekly_off_days
                if command.weekly_off_days
                else business.default_weekly_off_days
            )
            working_hours = (
                command.working_hours if command.working_hours else business.default_working_hours
            )

            employee = Employee.create(
                business_id=command.business_id,
                name=command.name,
                salary_type=command.salary_type,
                base_rate=command.base_rate,
                overtime_multiplier=overtime_multiplier,
                weekly_off_days=weekly_off_days,
                working_hours=working_hours,
                phone=command.phone,
                designation=command.designation,
                joining_date=command.joining_date,
            )
            await self.employee_repo.add(employee)
            return employee


@dataclass
class UpdateEmployeeUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: UpdateEmployeeCommand) -> Employee:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.current_user_id
            )

            employee = await get_owned_employee(self.employee_repo, command.employee_id, business)

            employee.update(
                name=command.name,
                salary_type=command.salary_type,
                base_rate=command.base_rate,
                overtime_multiplier=command.overtime_multiplier,
                weekly_off_days=command.weekly_off_days,
                working_hours=command.working_hours,
                phone=command.phone,
                designation=command.designation,
                joining_date=command.joining_date,
            )
            await self.employee_repo.update(employee)
            return employee


@dataclass
class DeleteEmployeeUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: DeleteEmployeeCommand) -> None:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.current_user_id
            )

            employee = await get_owned_employee(self.employee_repo, command.employee_id, business)

            await self.employee_repo.delete(employee)


@dataclass
class GetEmployeesUseCase:
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: GetEmployeesCommand) -> list[Employee]:
        business = await get_owned_business(
            self.business_repo, command.business_id, command.current_user_id
        )

        employees = await self.employee_repo.get_all_by_business_id(
            business.id, include_inactive=command.include_inactive
        )
        return employees


@dataclass
class GetEmployeeUseCase:
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: GetEmployeeCommand) -> Employee:
        business = await get_owned_business(
            self.business_repo, command.business_id, command.current_user_id
        )

        employee = await get_owned_employee(self.employee_repo, command.employee_id, business)
        return employee


@dataclass
class ActivateEmployeeUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: ActivateEmployeeCommand) -> Employee:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.current_user_id
            )

            employee = await get_owned_employee(self.employee_repo, command.employee_id, business)

            employee.activate()
            await self.employee_repo.update(employee)
            return employee


@dataclass
class DeactivateEmployeeUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort
    employee_repo: EmployeeRepositoryPort

    async def execute(self, command: DeactivateEmployeeCommand) -> Employee:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.current_user_id
            )

            employee = await get_owned_employee(self.employee_repo, command.employee_id, business)

            employee.deactivate()
            await self.employee_repo.update(employee)
            return employee
