from dataclasses import dataclass
from uuid import UUID

from app.features.auth.domain.entities import CurrentUser
from app.features.auth.domain.value_objects import UserRole
from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.domain.entities import Business
from app.features.business.domain.exceptions import (
    BusinessNotFoundError,
    InsufficientPermissionsError,
)


class BusinessAuthorizationService:
    def authorize_can_create_business(self, current_user: CurrentUser) -> None:
        if UserRole.OWNER not in current_user.roles:
            raise InsufficientPermissionsError(
                user_id=current_user.id, required_role=UserRole.OWNER
            )

    def authorize_is_owner(self, business: Business, current_user: CurrentUser) -> None:
        if business.owner_id != current_user.id:
            raise InsufficientPermissionsError(
                user_id=current_user.id, required_role=UserRole.OWNER
            )


@dataclass
class BusinessService:
    """Application service — the sole gateway to ``BusinessRepositoryPort``.

    Own-feature use cases depend on this concrete class. Cross-feature
    consumers declare their own narrow ``Protocol`` port (e.g.
    ``BusinessServicePort``) which this class satisfies structurally.
    """

    business_repo: BusinessRepositoryPort

    async def get_by_id(self, business_id: UUID) -> Business | None:
        return await self.business_repo.get_by_id(business_id)

    async def get_by_slug_and_owner(self, slug: str, owner_id: UUID) -> Business | None:
        return await self.business_repo.get_by_slug_and_owner(slug, owner_id)

    async def add(self, business: Business) -> None:
        await self.business_repo.add(business)

    async def update(self, business: Business) -> None:
        await self.business_repo.update(business)

    async def delete(self, business: Business) -> None:
        await self.business_repo.delete(business)

    async def list_by_owner(self, owner_id: UUID) -> list[Business]:
        return await self.business_repo.list_by_owner(owner_id)

    async def get_owned_business(self, business_id: UUID, owner_id: UUID) -> Business:
        """Fetch a business and verify it is owned by ``owner_id``.

        Raises ``BusinessNotFoundError`` if it does not exist, and
        ``BusinessNotOwnedError`` (via the entity invariant) if it exists but
        belongs to a different owner.
        """
        business = await self.business_repo.get_by_id(business_id)
        if not business:
            raise BusinessNotFoundError(business_id=business_id)
        business.ensure_owned_by(owner_id)
        return business
