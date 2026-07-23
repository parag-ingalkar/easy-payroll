from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.features.auth.domain.entities import CurrentUser, User
from app.features.auth.presentation.dependencies import get_current_user
from app.features.business.application.commands import (
    CreateBusinessCommand,
    DeleteBusinessCommand,
    ListBusinessesCommand,
    UpdateBusinessCommand,
)
from app.features.business.application.use_cases import (
    CreateBusinessUseCase,
    DeleteBusinessUseCase,
    ListBusinessesUseCase,
    UpdateBusinessUseCase,
)
from app.features.business.domain.entities import Business
from app.features.business.presentation.dependencies import (
    get_create_business_use_case,
    get_delete_business_use_case,
    get_list_businesses_use_case,
    get_update_business_use_case,
    verify_business_ownership,
)
from app.features.business.presentation.schemas import (
    BusinessResponse,
    CreateBusinessRequest,
    UpdateBusinessRequest,
)

router = APIRouter()


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    body: CreateBusinessRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: CreateBusinessUseCase = Depends(get_create_business_use_case),
) -> BusinessResponse:
    command = CreateBusinessCommand(
        current_user=current_user,
        name=body.name,
        divisor_policy=body.divisor_policy,
        default_overtime_multiplier=body.default_overtime_multiplier,
        default_weekly_off_days=body.default_weekly_off_days,
        default_working_hours=body.default_working_hours,
    )
    business = await use_case.execute(command)
    return BusinessResponse.model_validate(business)


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(
    current_user: CurrentUser = Depends(get_current_user),
    use_case: ListBusinessesUseCase = Depends(get_list_businesses_use_case),
) -> list[BusinessResponse]:
    command = ListBusinessesCommand(current_user=current_user)
    businesses = await use_case.execute(command)
    return [BusinessResponse.model_validate(business) for business in businesses]


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business: Business = Depends(verify_business_ownership),
) -> BusinessResponse:
    return BusinessResponse.model_validate(business)


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: UUID,
    body: UpdateBusinessRequest,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: UpdateBusinessUseCase = Depends(get_update_business_use_case),
) -> BusinessResponse:
    command = UpdateBusinessCommand(
        business_id=business_id,
        current_user=current_user,
        name=body.name,
        divisor_policy=body.divisor_policy,
        default_overtime_multiplier=body.default_overtime_multiplier,
        default_weekly_off_days=body.default_weekly_off_days,
        default_working_hours=body.default_working_hours,
    )
    business = await use_case.execute(command)
    return BusinessResponse.model_validate(business)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: DeleteBusinessUseCase = Depends(get_delete_business_use_case),
) -> None:
    command = DeleteBusinessCommand(
        business_id=business_id,
        current_user=current_user,
    )
    await use_case.execute(command)
