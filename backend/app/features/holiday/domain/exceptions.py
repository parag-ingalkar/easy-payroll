"""Holiday-domain exceptions."""

from app.core.exception_handler import ConflictError, NotFoundError


class HolidayNotFoundError(NotFoundError):
    code = "holiday_not_found"
    detail = "Holiday not found"

    def __init__(self, business_id: object, holiday_date: object) -> None:
        super().__init__(business_id=business_id, holiday_date=str(holiday_date))


class DuplicateHolidayError(ConflictError):
    code = "duplicate_holiday"
    detail = "A holiday already exists for this date"

    def __init__(self, business_id: object, holiday_date: object) -> None:
        super().__init__(business_id=business_id, holiday_date=str(holiday_date))
