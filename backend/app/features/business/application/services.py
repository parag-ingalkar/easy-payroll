from uuid import UUID

from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.domain.entities import Business
from app.features.business.domain.exceptions import BusinessNotFoundError


async def get_owned_business(
    business_repo: BusinessRepositoryPort, business_id: UUID, owner_id: UUID
) -> Business:
    business = await business_repo.get_by_id(business_id)
    if not business:
        raise BusinessNotFoundError(business_id=business_id)
    business.ensure_owned_by(owner_id)
    return business