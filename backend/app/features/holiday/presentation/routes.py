from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.features.auth.domain.entities import User
from app.features.auth.presentation.dependencies import get_current_user
from app.features.holiday.application.commands import (
    CreateHolidayCommand,
    DeleteHolidayCommand,
    GetHolidayCommand,
    ListHolidaysCommand,
)
from app.features.holiday.application.use_cases import (
    CreateHolidayUseCase,
    DeleteHolidayUseCase,
    GetHolidayUseCase,
    ListHolidaysUseCase,
)
from app.features.holiday.presentation.dependencies import (
    get_create_holiday_use_case,
    get_delete_holiday_use_case,
    get_get_holiday_use_case,
    get_list_holidays_use_case,
)
from app.features.holiday.presentation.schemas import (
    CreateHolidayRequest,
    HolidayResponse,
)

router = APIRouter()


@router.post("", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    body: CreateHolidayRequest,
    business_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: CreateHolidayUseCase = Depends(get_create_holiday_use_case),
) -> HolidayResponse:
    command = CreateHolidayCommand(
        business_id=business_id,
        owner_id=current_user.id,
        holiday_date=body.holiday_date,
        name=body.name,
        holiday_type=body.holiday_type,
        is_paid=body.is_paid,
    )
    holiday = await use_case.execute(command)
    return HolidayResponse.model_validate(holiday)


@router.get("", response_model=list[HolidayResponse])
async def list_holidays(
    business_id: UUID,
    year: int | None = None,
    month: int | None = None,
    current_user: User = Depends(get_current_user),
    use_case: ListHolidaysUseCase = Depends(get_list_holidays_use_case),
) -> list[HolidayResponse]:
    command = ListHolidaysCommand(
        business_id=business_id,
        owner_id=current_user.id,
        year=year,
        month=month,
    )
    holidays = await use_case.execute(command)
    return [HolidayResponse.model_validate(holiday) for holiday in holidays]


@router.get("/{holiday_date}", response_model=HolidayResponse)
async def get_holiday(
    business_id: UUID,
    holiday_date: date,
    current_user: User = Depends(get_current_user),
    use_case: GetHolidayUseCase = Depends(get_get_holiday_use_case),
) -> HolidayResponse:
    command = GetHolidayCommand(
        business_id=business_id,
        owner_id=current_user.id,
        holiday_date=holiday_date,
    )
    holiday = await use_case.execute(command)
    return HolidayResponse.model_validate(holiday)


@router.delete("/{holiday_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    business_id: UUID,
    holiday_date: date,
    current_user: User = Depends(get_current_user),
    use_case: DeleteHolidayUseCase = Depends(get_delete_holiday_use_case),
) -> None:
    command = DeleteHolidayCommand(
        business_id=business_id,
        owner_id=current_user.id,
        holiday_date=holiday_date,
    )
    await use_case.execute(command)
