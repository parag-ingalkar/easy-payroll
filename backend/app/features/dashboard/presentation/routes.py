"""Dashboard API route — single aggregate endpoint for the owner dashboard."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.features.auth.domain.entities import CurrentUser
from app.features.auth.presentation.dependencies import get_current_user
from app.features.dashboard.application.services import DashboardService
from app.features.dashboard.presentation.dependencies import get_dashboard_service
from app.features.dashboard.presentation.schemas import DashboardResponse

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    business_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    """Return the aggregated dashboard payload for a business."""
    data = await service.get_dashboard(business_id, current_user.id)
    return DashboardResponse.model_validate(data)
