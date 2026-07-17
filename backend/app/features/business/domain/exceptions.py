"""Business-domain exceptions."""

from app.core.exception_handler import ConflictError, ForbiddenError, NotFoundError


class BusinessNotFoundError(NotFoundError):
    code = "business_not_found"
    detail = "Business not found"

    def __init__(self, business_id: object) -> None:
        super().__init__(business_id=business_id)


class BusinessNotOwnedError(ForbiddenError):
    code = "business_not_owned"
    detail = "You do not own this business"

    def __init__(self, business_id: object, owner_id: object) -> None:
        super().__init__(business_id=business_id, owner_id=owner_id)


class DuplicateBusinessError(ConflictError):
    code = "duplicate_business"
    detail = "A business with this name already exists for this owner"

    def __init__(self, slug: object) -> None:
        super().__init__(slug=slug)
