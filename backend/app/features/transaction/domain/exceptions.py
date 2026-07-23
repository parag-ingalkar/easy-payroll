"""Transaction-domain exceptions."""

from app.core.exception_handler import ForbiddenError, NotFoundError, ValidationError


class TransactionNotFoundError(NotFoundError):
    code = "transaction_not_found"
    detail = "Transaction not found"

    def __init__(self, transaction_id: object) -> None:
        super().__init__(transaction_id=transaction_id)


class TransactionNotOwnedError(ForbiddenError):
    code = "transaction_not_owned"
    detail = "Transaction does not belong to this employee"

    def __init__(self, transaction_id: object, employee_id: object) -> None:
        super().__init__(transaction_id=transaction_id, employee_id=employee_id)


class InvalidTransactionAmountError(ValidationError):
    code = "invalid_transaction_amount"
    detail = "Transaction amount must be greater than zero"

    def __init__(self, amount: object) -> None:
        super().__init__(amount=str(amount))
