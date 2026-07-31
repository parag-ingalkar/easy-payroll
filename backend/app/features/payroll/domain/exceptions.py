"""Payroll-domain exceptions."""

from app.core.exception_handler import ConflictError, ForbiddenError, NotFoundError


class PayrollRunNotFoundError(NotFoundError):
    code = "payroll_run_not_found"
    detail = "Payroll run not found"

    def __init__(self, payroll_id: object) -> None:
        super().__init__(payroll_id=payroll_id)


class PayrollRunNotOwnedError(ForbiddenError):
    code = "payroll_run_not_owned"
    detail = "Payroll run does not belong to this business"

    def __init__(self, payroll_id: object, business_id: object) -> None:
        super().__init__(payroll_id=payroll_id, business_id=business_id)


class PayrollRunAlreadyExistsError(ConflictError):
    code = "payroll_run_already_exists"
    detail = "A payroll run already exists for this business, year and month"

    def __init__(self, business_id: object, year: object, month: object) -> None:
        super().__init__(business_id=business_id, year=year, month=month)


class PayrollAlreadyFinalizedError(ConflictError):
    code = "payroll_already_finalized"
    detail = "Payroll run is already finalized and cannot be modified"

    def __init__(self, payroll_id: object) -> None:
        super().__init__(payroll_id=payroll_id)


class PayrollLineItemNotFoundError(NotFoundError):
    code = "payroll_line_item_not_found"
    detail = "Payroll line item not found"

    def __init__(self, line_item_id: object) -> None:
        super().__init__(line_item_id=line_item_id)


class PayrollLineItemNotOwnedError(ForbiddenError):
    code = "payroll_line_item_not_owned"
    detail = "Payroll line item does not belong to this run"

    def __init__(self, line_item_id: object, run_id: object) -> None:
        super().__init__(line_item_id=line_item_id, run_id=run_id)


class PayrollLineItemAlreadyPaidError(ConflictError):
    code = "payroll_line_item_already_paid"
    detail = "Payroll line item is already marked as paid"

    def __init__(self, line_item_id: object) -> None:
        super().__init__(line_item_id=line_item_id)
