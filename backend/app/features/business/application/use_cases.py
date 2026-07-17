from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.business.application.commands import (
    CreateBusinessCommand,
    DeleteBusinessCommand,
    UpdateBusinessCommand,
)
from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.application.services import get_owned_business
from app.features.business.domain.entities import Business
from app.features.business.domain.exceptions import (
    DuplicateBusinessError,
)


@dataclass
class CreateBusinessUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort

    async def execute(self, command: CreateBusinessCommand) -> Business:
        business = Business.create(
            owner_id=command.owner_id,
            name=command.name,
            divisor_policy=command.divisor_policy,
            default_overtime_multiplier=command.default_overtime_multiplier,
            default_weekly_off_days=command.default_weekly_off_days,
            default_working_hours=command.default_working_hours,
        )
        async with self.uow:
            existing_business = await self.business_repo.get_by_slug(
                business.slug
            )  # Check for slug uniqueness
            if existing_business:
                raise DuplicateBusinessError(slug=business.slug)

            await self.business_repo.add(business)
            return business


@dataclass
class UpdateBusinessUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort

    async def execute(self, command: UpdateBusinessCommand) -> Business:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.owner_id
            )

            business.update(
                name=command.name,
                divisor_policy=command.divisor_policy,
                default_overtime_multiplier=command.default_overtime_multiplier,
                default_weekly_off_days=command.default_weekly_off_days,
                default_working_hours=command.default_working_hours,
            )
            await self.business_repo.update(business)
            return business


@dataclass
class DeleteBusinessUseCase:
    uow: AbstractUnitOfWork
    business_repo: BusinessRepositoryPort

    async def execute(self, command: DeleteBusinessCommand) -> None:
        async with self.uow:
            business = await get_owned_business(
                self.business_repo, command.business_id, command.owner_id
            )

            await self.business_repo.delete(business)
