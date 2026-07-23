from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.features.auth.domain.entities import CurrentUser
from app.features.auth.presentation.dependencies import get_current_user
from app.features.transaction.application.commands import (
    CreateTransactionCommand,
    DeleteTransactionCommand,
    GetTransactionCommand,
    GetTransactionsCommand,
    UpdateTransactionCommand,
)
from app.features.transaction.application.use_cases import (
    CreateTransactionUseCase,
    DeleteTransactionUseCase,
    GetTransactionsUseCase,
    GetTransactionUseCase,
    UpdateTransactionUseCase,
)
from app.features.transaction.presentation.dependencies import (
    get_create_transaction_use_case,
    get_delete_transaction_use_case,
    get_get_transaction_use_case,
    get_get_transactions_use_case,
    get_update_transaction_use_case,
)
from app.features.transaction.presentation.schemas import (
    CreateTransactionRequest,
    TransactionResponse,
    UpdateTransactionRequest,
)

router = APIRouter()


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    business_id: UUID,
    employee_id: UUID,
    body: CreateTransactionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case),
) -> TransactionResponse:
    command = CreateTransactionCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        transaction_date=body.transaction_date,
        type=body.type,
        amount=body.amount,
        description=body.description,
    )
    transaction = await use_case.execute(command)
    return TransactionResponse.model_validate(transaction)


@router.get("", response_model=list[TransactionResponse])
async def get_transactions(
    business_id: UUID,
    employee_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: GetTransactionsUseCase = Depends(get_get_transactions_use_case),
) -> list[TransactionResponse]:
    command = GetTransactionsCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
    )
    transactions = await use_case.execute(command)
    return [TransactionResponse.model_validate(transaction) for transaction in transactions]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    business_id: UUID,
    employee_id: UUID,
    transaction_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: GetTransactionUseCase = Depends(get_get_transaction_use_case),
) -> TransactionResponse:
    command = GetTransactionCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        transaction_id=transaction_id,
    )
    transaction = await use_case.execute(command)
    return TransactionResponse.model_validate(transaction)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    business_id: UUID,
    employee_id: UUID,
    transaction_id: UUID,
    body: UpdateTransactionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: UpdateTransactionUseCase = Depends(get_update_transaction_use_case),
) -> TransactionResponse:
    command = UpdateTransactionCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        transaction_id=transaction_id,
        transaction_date=body.transaction_date,
        type=body.type,
        amount=body.amount,
        description=body.description,
    )
    transaction = await use_case.execute(command)
    return TransactionResponse.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    business_id: UUID,
    employee_id: UUID,
    transaction_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: DeleteTransactionUseCase = Depends(get_delete_transaction_use_case),
) -> None:
    command = DeleteTransactionCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        transaction_id=transaction_id,
    )
    await use_case.execute(command)
