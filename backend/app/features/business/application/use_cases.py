from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.business.application.commands import (
    CreateBusinessCommand,
    DeleteBusinessCommand,
    ListBusinessesCommand,
    UpdateBusinessCommand,
)
from app.features.business.application.services import (
    BusinessAuthorizationService,
    BusinessService,
)
from app.features.business.domain.entities import Business
from app.features.business.domain.exceptions import (
    BusinessNotFoundError,
    DuplicateBusinessError,
)


@dataclass
class CreateBusinessUseCase:
    uow: AbstractUnitOfWork
    business_service: BusinessService
    auth_service: BusinessAuthorizationService = BusinessAuthorizationService()

    async def execute(self, command: CreateBusinessCommand) -> Business:
        async with self.uow:
            self.auth_service.authorize_can_create_business(command.current_user)

            business = Business.create(
                owner_id=command.current_user.id,
                name=command.name,
                divisor_policy=command.divisor_policy,
                default_overtime_multiplier=command.default_overtime_multiplier,
                default_weekly_off_days=command.default_weekly_off_days,
                default_working_hours=command.default_working_hours,
            )
            existing_business = await self.business_service.get_by_slug_and_owner(
                business.slug, business.owner_id
            )  # Check for slug uniqueness
            if existing_business:
                raise DuplicateBusinessError(slug=business.slug)

            await self.business_service.add(business)
            return business


@dataclass
class UpdateBusinessUseCase:
    uow: AbstractUnitOfWork
    business_service: BusinessService
    auth_service: BusinessAuthorizationService = BusinessAuthorizationService()

    async def execute(self, command: UpdateBusinessCommand) -> Business:
        async with self.uow:
            business = await self.business_service.get_by_id(command.business_id)
            if not business:
                raise BusinessNotFoundError(business_id=command.business_id)

            self.auth_service.authorize_is_owner(business, command.current_user)

            business.update(
                name=command.name,
                divisor_policy=command.divisor_policy,
                default_overtime_multiplier=command.default_overtime_multiplier,
                default_weekly_off_days=command.default_weekly_off_days,
                default_working_hours=command.default_working_hours,
            )
            await self.business_service.update(business)
            return business


@dataclass
class DeleteBusinessUseCase:
    uow: AbstractUnitOfWork
    business_service: BusinessService
    auth_service: BusinessAuthorizationService = BusinessAuthorizationService()

    async def execute(self, command: DeleteBusinessCommand) -> None:
        async with self.uow:
            business = await self.business_service.get_by_id(command.business_id)
            if not business:
                raise BusinessNotFoundError(business_id=command.business_id)

            self.auth_service.authorize_is_owner(business, command.current_user)

            await self.business_service.delete(business)


@dataclass
class ListBusinessesUseCase:
    business_service: BusinessService

    async def execute(self, command: ListBusinessesCommand) -> list[Business]:
        businesses = await self.business_service.list_by_owner(command.current_user.id)
        return businesses
