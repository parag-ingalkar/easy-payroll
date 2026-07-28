"""Attendance API routes.

Two routers are exported and mounted under different prefixes in
``app/core/router.py``:

* ``router`` — employee-scoped: one employee, many days. Mounted at
  ``/business/{business_id}/employees/{employee_id}/attendances``. Supports
  PUT/GET/DELETE by date plus a one-employee bulk (many days).
* ``business_attendance_router`` — business-scoped: one date, many employees.
  Mounted at ``/business/{business_id}/attendances``. Supports the
  "mark all present" bulk and loading current state for a date.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.features.attendance.application.commands import (
    BulkBusinessAttendanceCommand,
    BulkBusinessAttendanceEntry,
    BulkEmployeeAttendanceCommand,
    BulkEmployeeAttendanceEntry,
    DeleteAttendanceCommand,
    GetAttendanceCommand,
    ListBusinessAttendanceCommand,
    ListEmployeeAttendanceCommand,
    UpsertAttendanceCommand,
)
from app.features.attendance.application.use_cases import (
    BulkBusinessAttendanceUseCase,
    BulkEmployeeAttendanceUseCase,
    DeleteAttendanceUseCase,
    GetAttendanceUseCase,
    ListBusinessAttendanceUseCase,
    ListEmployeeAttendanceUseCase,
    UpsertAttendanceUseCase,
)
from app.features.attendance.presentation.dependencies import (
    get_bulk_business_attendance_use_case,
    get_bulk_employee_attendance_use_case,
    get_delete_attendance_use_case,
    get_get_attendance_use_case,
    get_list_business_attendance_use_case,
    get_list_employee_attendance_use_case,
    get_upsert_attendance_use_case,
)
from app.features.attendance.presentation.schemas import (
    AttendanceResponse,
    BulkBusinessAttendanceRequest,
    BulkEmployeeAttendanceRequest,
    UpsertAttendanceRequest,
)
from app.features.auth.domain.entities import CurrentUser
from app.features.auth.presentation.dependencies import get_current_user

router = APIRouter()
business_attendance_router = APIRouter()


# --- employee-scoped (one employee, many days) -----------------------------


@router.put(
    "/{attendance_date}",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
)
async def upsert_attendance(
    business_id: UUID,
    employee_id: UUID,
    attendance_date: date,
    body: UpsertAttendanceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: UpsertAttendanceUseCase = Depends(get_upsert_attendance_use_case),
) -> AttendanceResponse:
    """Full-replace upsert of one day's attendance (keyed by employee + date)."""
    command = UpsertAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        attendance_date=attendance_date,
        status=body.status,
        overtime_hours=body.overtime_hours,
    )
    record = await use_case.execute(command)
    return AttendanceResponse.model_validate(record)


@router.get("/{attendance_date}", response_model=AttendanceResponse)
async def get_attendance(
    business_id: UUID,
    employee_id: UUID,
    attendance_date: date,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: GetAttendanceUseCase = Depends(get_get_attendance_use_case),
) -> AttendanceResponse:
    command = GetAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        attendance_date=attendance_date,
    )
    record = await use_case.execute(command)
    return AttendanceResponse.model_validate(record)


@router.get("", response_model=list[AttendanceResponse])
async def list_employee_attendance(
    business_id: UUID,
    employee_id: UUID,
    year: int | None = None,
    month: int | None = None,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: ListEmployeeAttendanceUseCase = Depends(get_list_employee_attendance_use_case),
) -> list[AttendanceResponse]:
    command = ListEmployeeAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        year=year,
        month=month,
    )
    records = await use_case.execute(command)
    return [AttendanceResponse.model_validate(r) for r in records]


@router.delete("/{attendance_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    business_id: UUID,
    employee_id: UUID,
    attendance_date: date,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: DeleteAttendanceUseCase = Depends(get_delete_attendance_use_case),
) -> None:
    command = DeleteAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        attendance_date=attendance_date,
    )
    await use_case.execute(command)


@router.put("/bulk", response_model=list[AttendanceResponse])
async def bulk_employee_attendance(
    business_id: UUID,
    employee_id: UUID,
    body: BulkEmployeeAttendanceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: BulkEmployeeAttendanceUseCase = Depends(get_bulk_employee_attendance_use_case),
) -> list[AttendanceResponse]:
    """Mark attendance for one employee across multiple days."""
    command = BulkEmployeeAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        employee_id=employee_id,
        entries=[
            BulkEmployeeAttendanceEntry(
                date=e.date, status=e.status, overtime_hours=e.overtime_hours
            )
            for e in body.entries
        ],
    )
    records = await use_case.execute(command)
    return [AttendanceResponse.model_validate(r) for r in records]


# --- business-scoped (one date, many employees) ----------------------------


@business_attendance_router.put("/bulk", response_model=list[AttendanceResponse])
async def bulk_business_attendance(
    business_id: UUID,
    attendance_date: date,
    body: BulkBusinessAttendanceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: BulkBusinessAttendanceUseCase = Depends(get_bulk_business_attendance_use_case),
) -> list[AttendanceResponse]:
    """Mark attendance for multiple employees on a single date.

    Useful for "mark all employees as present" — the client supplies one entry
    per employee.
    """
    command = BulkBusinessAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        attendance_date=attendance_date,
        entries=[
            BulkBusinessAttendanceEntry(
                employee_id=e.employee_id,
                status=e.status,
                overtime_hours=e.overtime_hours,
            )
            for e in body.entries
        ],
    )
    records = await use_case.execute(command)
    return [AttendanceResponse.model_validate(r) for r in records]


@business_attendance_router.get(
    "/by-date/{attendance_date}", response_model=list[AttendanceResponse]
)
async def list_business_attendance(
    business_id: UUID,
    attendance_date: date,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: ListBusinessAttendanceUseCase = Depends(get_list_business_attendance_use_case),
) -> list[AttendanceResponse]:
    """Load current attendance state for every employee of a business on a date."""
    command = ListBusinessAttendanceCommand(
        current_user=current_user,
        business_id=business_id,
        attendance_date=attendance_date,
    )
    records = await use_case.execute(command)
    return [AttendanceResponse.model_validate(r) for r in records]
