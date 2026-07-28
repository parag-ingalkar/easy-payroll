"""Attendance-domain exceptions."""

from app.core.exception_handler import ForbiddenError, NotFoundError, ValidationError


class AttendanceNotFoundError(NotFoundError):
    code = "attendance_not_found"
    detail = "Attendance record not found"

    def __init__(self, employee_id: object, attendance_date: object) -> None:
        super().__init__(employee_id=employee_id, attendance_date=attendance_date)


class AttendanceNotOwnedError(ForbiddenError):
    code = "attendance_not_owned"
    detail = "Attendance record does not belong to this employee"

    def __init__(self, attendance_id: object, employee_id: object) -> None:
        super().__init__(attendance_id=attendance_id, employee_id=employee_id)


class InvalidOvertimeHoursError(ValidationError):
    code = "invalid_overtime_hours"
    detail = "Overtime hours cannot be negative"

    def __init__(self, overtime_hours: object) -> None:
        super().__init__(overtime_hours=str(overtime_hours))


class CannotMarkAttendance(ValidationError):
    code = "cannot_mark_attendance"
    detail = "Cannot mark attendance for this employee on this date"

    def __init__(self, attendance_date: object) -> None:
        super().__init__(attendance_date=attendance_date)