from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.employee.application.commands import (
    ActivateEmployeeCommand,
    CreateEmployeeCommand,
    DeactivateEmployeeCommand,
    DeleteEmployeeCommand,
    GetEmployeeCommand,
    GetEmployeesCommand,
    UpdateEmployeeCommand,
)
from app.features.employee.application.ports import BusinessServicePort
from app.features.employee.application.services import EmployeeService
from app.features.employee.domain.entities import Employee
from app.features.employee.domain.exceptions import (
    EmployeeAlreadyExistsError,
)


@dataclass
class CreateEmployeeUseCase:
    uow: AbstractUnitOfWork
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: CreateEmployeeCommand) -> Employee:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )

            existing_employee = await self.employee_service.get_by_business_and_name(
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
            await self.employee_service.add(employee)
            return employee


@dataclass
class UpdateEmployeeUseCase:
    uow: AbstractUnitOfWork
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: UpdateEmployeeCommand) -> Employee:
        async with self.uow:
            employee = await self.employee_service.get_by_id_or_raise(command.employee_id)
            await self.business_service.get_owned_business(
                employee.business_id, command.current_user.id
            )

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
            await self.employee_service.update(employee)
            return employee


@dataclass
class DeleteEmployeeUseCase:
    uow: AbstractUnitOfWork
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: DeleteEmployeeCommand) -> None:
        async with self.uow:
            employee = await self.employee_service.get_by_id_or_raise(command.employee_id)
            await self.business_service.get_owned_business(
                employee.business_id, command.current_user.id
            )

            await self.employee_service.delete(employee)


@dataclass
class GetEmployeesUseCase:
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: GetEmployeesCommand) -> list[Employee]:
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )

        return await self.employee_service.list_by_business(
            business.id, include_inactive=command.include_inactive
        )


@dataclass
class GetEmployeeUseCase:
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: GetEmployeeCommand) -> Employee:
        employee = await self.employee_service.get_by_id_or_raise(command.employee_id)
        await self.business_service.get_owned_business(
            employee.business_id, command.current_user.id
        )
        return employee


@dataclass
class ActivateEmployeeUseCase:
    uow: AbstractUnitOfWork
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: ActivateEmployeeCommand) -> Employee:
        async with self.uow:
            employee = await self.employee_service.get_by_id_or_raise(command.employee_id)
            await self.business_service.get_owned_business(
                employee.business_id, command.current_user.id
            )

            employee.activate()
            await self.employee_service.update(employee)
            return employee


@dataclass
class DeactivateEmployeeUseCase:
    uow: AbstractUnitOfWork
    employee_service: EmployeeService
    business_service: BusinessServicePort

    async def execute(self, command: DeactivateEmployeeCommand) -> Employee:
        async with self.uow:
            employee = await self.employee_service.get_by_id_or_raise(command.employee_id)
            await self.business_service.get_owned_business(
                employee.business_id, command.current_user.id
            )

            employee.deactivate()
            await self.employee_service.update(employee)
            return employee
