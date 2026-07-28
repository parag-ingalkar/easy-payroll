from datetime import UTC, date, datetime

from app.shared.enums import WeekDay

int_to_weekday = {
    0: WeekDay.MONDAY,
    1: WeekDay.TUESDAY,
    2: WeekDay.WEDNESDAY,
    3: WeekDay.THURSDAY,
    4: WeekDay.FRIDAY,
    5: WeekDay.SATURDAY,
    6: WeekDay.SUNDAY,
}


def get_now() -> datetime:
    return datetime.now(UTC)


def get_weekday(date: date) -> WeekDay:
    """Return the weekday of a given date, where Monday is 0 and Sunday is 6."""

    return int_to_weekday[date.weekday()]
