from typing import Protocol
from uuid import UUID

from app.features.business.domain.entities import Business


class BusinessRepositoryPort(Protocol):
    async def get_by_id(self, business_id: UUID) -> Business | None:
        """Fetches a business by its ID."""
        ...

    async def get_by_id_and_owner_id(self, business_id: UUID, owner_id: UUID) -> Business | None:
        """Fetches a business by its ID and owner ID."""
        ...

    async def get_by_slug(self, slug: str) -> Business | None:
        """Fetches a business by its slug."""
        ...

    async def add(self, business: Business) -> None:
        """Adds a new business to the repository."""
        ...

    async def update(self, business: Business) -> None:
        """Updates an existing business in the repository."""
        ...

    async def delete(self, business: Business) -> None:
        """Deletes a business from the repository."""
        ...
