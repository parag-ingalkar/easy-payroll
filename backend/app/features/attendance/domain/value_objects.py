"""Attendance-domain categorical values (ADR-006: StrEnum throughout)."""

from enum import StrEnum


class AttendanceStatus(StrEnum):
    """The status of a single day's attendance for an employee.

    Consumed by the payroll engine (see payroll/domain/services.py). Days with
    no explicit record are derived in the payroll engine — paid holidays count
    as full paid days and weekly-off days are excluded from missing-day
    warnings (PRODUCT.md → Attendance States, ADR-022).
    """

    PRESENT = "present"
    PAID_LEAVE = "paid_leave"
    UNPAID_LEAVE = "unpaid_leave"
    HALF_DAY = "half_day"
