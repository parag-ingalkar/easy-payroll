from app.core.exception_handler import ConflictError, NotFoundError


class HolidayNotFoundError(NotFoundError):
    detail = "Holiday not found"


class DuplicateHolidayError(ConflictError):
    detail = "A holiday already exists for this business on this date"
