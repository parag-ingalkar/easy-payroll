from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.domain.entities import Business
from app.features.business.infrastructure.models import BusinessModel


class SQLBusinessRepository(BusinessRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, business_id: UUID) -> Business | None:
        """Fetches a business by its ID."""
        result = await self.session.get(BusinessModel, business_id)
        return result.to_domain() if result else None

    async def get_by_id_and_owner_id(self, business_id: UUID, owner_id: UUID) -> Business | None:
        """Fetches a business by its ID and owner ID."""
        result = await self.session.execute(
            select(BusinessModel).where(
                BusinessModel.id == business_id, BusinessModel.owner_id == owner_id
            )
        )
        business_model = result.scalar_one_or_none()
        return business_model.to_domain() if business_model else None

    async def get_by_slug(self, slug: str) -> Business | None:
        """Fetches a business by its slug."""
        result = await self.session.execute(select(BusinessModel).where(BusinessModel.slug == slug))
        business_model = result.scalar_one_or_none()
        return business_model.to_domain() if business_model else None

    async def add(self, business: Business) -> None:
        """Adds a new business to the repository."""
        business_model = BusinessModel.from_domain(business)
        self.session.add(business_model)
        await self.session.flush()  # Ensure the business is persisted and ID is generated

    async def update(self, business: Business) -> None:
        """Updates an existing business in the repository."""
        model = BusinessModel.from_domain(business)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, business: Business) -> None:
        """Deletes a business from the repository."""
        model = await self.session.get(BusinessModel, business.id)
        if model is None:
            return
        await self.session.delete(model)
