from collections.abc import Sequence
from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.holiday.application.commands import (
    CreateHolidayCommand,
    DeleteHolidayCommand,
    GetHolidayCommand,
    ListHolidaysCommand,
)
from app.features.holiday.application.ports import BusinessServicePort
from app.features.holiday.application.services import HolidayService
from app.features.holiday.domain.entities import Holiday
from app.features.holiday.domain.exceptions import (
    DuplicateHolidayError,
)


@dataclass
class CreateHolidayUseCase:
    uow: AbstractUnitOfWork
    holiday_service: HolidayService
    business_service: BusinessServicePort

    async def execute(self, command: CreateHolidayCommand) -> Holiday:
        async with self.uow:
            # Check business existence and ownership
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )

            # Check for duplicate holiday
            existing_holiday = await self.holiday_service.get_by_business_and_date(
                business.id, command.holiday_date
            )
            if existing_holiday:
                raise DuplicateHolidayError(command.business_id, command.holiday_date)

            holiday = Holiday.create(
                business_id=business.id,
                holiday_date=command.holiday_date,
                name=command.name,
                holiday_type=command.holiday_type,
                is_paid=command.is_paid,
            )

            await self.holiday_service.add(holiday)
            return holiday


@dataclass
class DeleteHolidayUseCase:
    uow: AbstractUnitOfWork
    holiday_service: HolidayService
    business_service: BusinessServicePort

    async def execute(self, command: DeleteHolidayCommand) -> None:
        async with self.uow:
            # Check business existence and ownership
            business = await self.business_service.get_owned_business(
                command.business_id, command.current_user.id
            )

            holiday = await self.holiday_service.get_or_raise(
                business.id, command.holiday_date
            )

            await self.holiday_service.delete(holiday)


@dataclass
class GetHolidayUseCase:
    holiday_service: HolidayService
    business_service: BusinessServicePort

    async def execute(self, command: GetHolidayCommand) -> Holiday:
        # Check business existence and ownership
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )

        return await self.holiday_service.get_or_raise(business.id, command.holiday_date)


@dataclass
class ListHolidaysUseCase:
    holiday_service: HolidayService
    business_service: BusinessServicePort

    async def execute(self, command: ListHolidaysCommand) -> Sequence[Holiday]:
        # Check business existence and ownership
        business = await self.business_service.get_owned_business(
            command.business_id, command.current_user.id
        )

        return await self.holiday_service.list_by_business(
            business.id, command.year, command.month
        )
