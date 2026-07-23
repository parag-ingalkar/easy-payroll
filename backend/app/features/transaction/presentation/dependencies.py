from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.business.application.services import BusinessService
from app.features.business.infrastructure.repositories import SQLBusinessRepository
from app.features.employee.application.services import EmployeeService
from app.features.employee.infrastructure.repositories import SQLEmployeeRepository
from app.features.transaction.application.services import TransactionService
from app.features.transaction.application.use_cases import (
    CreateTransactionUseCase,
    DeleteTransactionUseCase,
    GetTransactionsUseCase,
    GetTransactionUseCase,
    UpdateTransactionUseCase,
)
from app.features.transaction.infrastructure.repositories import SQLTransactionRepository


def get_create_transaction_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    transaction_service = TransactionService(SQLTransactionRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return CreateTransactionUseCase(
        uow=uow,
        transaction_service=transaction_service,
        employee_service=employee_service,
        business_service=business_service,
    )


def get_update_transaction_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    transaction_service = TransactionService(SQLTransactionRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return UpdateTransactionUseCase(
        uow=uow,
        transaction_service=transaction_service,
        employee_service=employee_service,
        business_service=business_service,
    )


def get_delete_transaction_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    transaction_service = TransactionService(SQLTransactionRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return DeleteTransactionUseCase(
        uow=uow,
        transaction_service=transaction_service,
        employee_service=employee_service,
        business_service=business_service,
    )


def get_get_transactions_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    transaction_service = TransactionService(SQLTransactionRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return GetTransactionsUseCase(
        transaction_service=transaction_service,
        employee_service=employee_service,
        business_service=business_service,
    )


def get_get_transaction_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    transaction_service = TransactionService(SQLTransactionRepository(db_session))
    employee_service = EmployeeService(SQLEmployeeRepository(db_session))
    business_service = BusinessService(SQLBusinessRepository(db_session))
    return GetTransactionUseCase(
        transaction_service=transaction_service,
        employee_service=employee_service,
        business_service=business_service,
    )
