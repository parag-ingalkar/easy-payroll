from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.transaction.application.commands import (
    CreateTransactionCommand,
    DeleteTransactionCommand,
    GetTransactionCommand,
    GetTransactionsCommand,
    UpdateTransactionCommand,
)
from app.features.transaction.application.ports import (
    BusinessServicePort,
    EmployeeServicePort,
)
from app.features.transaction.application.services import TransactionService
from app.features.transaction.domain.entities import Transaction


@dataclass
class CreateTransactionUseCase:
    uow: AbstractUnitOfWork
    transaction_service: TransactionService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: CreateTransactionCommand) -> Transaction:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            employee = await self.employee_service.get_owned_employee(
                command.employee_id, business.id
            )

            transaction = Transaction.create(
                employee_id=employee.id,
                transaction_date=command.transaction_date,
                type=command.type,
                amount=command.amount,
                description=command.description,
            )
            await self.transaction_service.add(transaction)
            return transaction


@dataclass
class UpdateTransactionUseCase:
    uow: AbstractUnitOfWork
    transaction_service: TransactionService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: UpdateTransactionCommand) -> Transaction:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            employee = await self.employee_service.get_owned_employee(
                command.employee_id, business.id
            )

            transaction = await self.transaction_service.get_owned_transaction(
                command.transaction_id, employee
            )

            transaction.update(
                transaction_date=command.transaction_date,
                type=command.type,
                amount=command.amount,
                description=command.description,
            )
            await self.transaction_service.update(transaction)
            return transaction


@dataclass
class DeleteTransactionUseCase:
    uow: AbstractUnitOfWork
    transaction_service: TransactionService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: DeleteTransactionCommand) -> None:
        async with self.uow:
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )
            employee = await self.employee_service.get_owned_employee(
                command.employee_id, business.id
            )

            transaction = await self.transaction_service.get_owned_transaction(
                command.transaction_id, employee
            )

            await self.transaction_service.delete(transaction)


@dataclass
class GetTransactionsUseCase:
    transaction_service: TransactionService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: GetTransactionsCommand) -> list[Transaction]:
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )
        employee = await self.employee_service.get_owned_employee(
            command.employee_id, business.id
        )

        return await self.transaction_service.get_all_by_employee_id(employee.id)


@dataclass
class GetTransactionUseCase:
    transaction_service: TransactionService
    business_service: BusinessServicePort
    employee_service: EmployeeServicePort

    async def execute(self, command: GetTransactionCommand) -> Transaction:
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )
        employee = await self.employee_service.get_owned_employee(
            command.employee_id, business.id
        )

        return await self.transaction_service.get_owned_transaction(
            command.transaction_id, employee
        )
