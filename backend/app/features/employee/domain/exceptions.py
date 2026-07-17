"""Employee-domain exceptions."""

from app.core.exception_handler import ConflictError, ForbiddenError, NotFoundError


class EmployeeNotFoundError(NotFoundError):
    code = "employee_not_found"
    detail = "Employee not found"

    def __init__(self, employee_id: object) -> None:
        super().__init__(employee_id=employee_id)


class EmployeeNotOwnedError(ForbiddenError):
    code = "employee_not_owned"
    detail = "Employee does not belong to this business"

    def __init__(self, employee_id: object, business_id: object) -> None:
        super().__init__(employee_id=employee_id, business_id=business_id)


class EmployeeAlreadyInactiveError(ConflictError):
    code = "employee_already_inactive"
    detail = "Employee is already inactive"

    def __init__(self, employee_id: object) -> None:
        super().__init__(employee_id=employee_id)


class EmployeeAlreadyActiveError(ConflictError):
    code = "employee_already_active"
    detail = "Employee is already active"

    def __init__(self, employee_id: object) -> None:
        super().__init__(employee_id=employee_id)


class EmployeeAlreadyExistsError(ConflictError):
    code = "employee_already_exists"
    detail = "An employee with this name already exists for this business"

    def __init__(self, business_id: object, name: str) -> None:
        super().__init__(business_id=business_id, name=name)
