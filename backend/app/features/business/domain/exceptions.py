"""Business-domain exceptions."""

from app.core.exception_handler import ConflictError, ForbiddenError, NotFoundError


class BusinessNotFoundError(NotFoundError):
    detail = "Business not found"


class BusinessNotOwnedError(ForbiddenError):
    detail = "You do not own this business"


class DuplicateBusinessError(ConflictError):
    detail = "A business with this name already exists for this owner"


class HolidayNotFound(NotFoundError):
    detail = "Holiday not found"


class HolidayDateConflict(ConflictError):
    detail = "A holiday already exists for this business on this date"
