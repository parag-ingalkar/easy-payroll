from collections.abc import Sequence
from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.application.services import get_owned_business
from app.features.holiday.application.commands import (
    CreateHolidayCommand,
    DeleteHolidayCommand,
    GetHolidayCommand,
    ListHolidaysCommand,
)
from app.features.holiday.application.ports import HolidaysRepositoryPort
from app.features.holiday.domain.entities import Holiday
from app.features.holiday.domain.exceptions import (
    DuplicateHolidayError,
    HolidayNotFoundError,
)


@dataclass
class CreateHolidayUseCase:
    uow: AbstractUnitOfWork
    holiday_repo: HolidaysRepositoryPort
    business_repo: BusinessRepositoryPort

    async def execute(self, command: CreateHolidayCommand) -> Holiday:
        async with self.uow:
            # Check business existence and ownership
            business = await get_owned_business(
                self.business_repo, command.business_id, command.owner_id
            )

            # Check for duplicate holiday
            existing_holiday = await self.holiday_repo.get_by_business_id_and_date(
                command.business_id, command.holiday_date
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

            await self.holiday_repo.add(holiday)
            return holiday


@dataclass
class DeleteHolidayUseCase:
    uow: AbstractUnitOfWork
    holiday_repo: HolidaysRepositoryPort
    business_repo: BusinessRepositoryPort

    async def execute(self, command: DeleteHolidayCommand) -> None:
        async with self.uow:
            # Check business existence and ownership
            business = await get_owned_business(
                self.business_repo, command.business_id, command.owner_id
            )

            # Check if the holiday exists
            holiday = await self.holiday_repo.get_by_business_id_and_date(
                business.id, command.holiday_date
            )
            if not holiday:
                raise HolidayNotFoundError(business.id, command.holiday_date)

            await self.holiday_repo.delete(holiday)


@dataclass
class GetHolidayUseCase:
    holiday_repo: HolidaysRepositoryPort
    business_repo: BusinessRepositoryPort

    async def execute(self, command: GetHolidayCommand) -> Holiday:
        # Check business existence and ownership
        business = await get_owned_business(
            self.business_repo, command.business_id, command.owner_id
        )

        holiday = await self.holiday_repo.get_by_business_id_and_date(
            business.id, command.holiday_date
        )
        if not holiday:
            raise HolidayNotFoundError(business.id, command.holiday_date)

        return holiday


@dataclass
class ListHolidaysUseCase:
    holiday_repo: HolidaysRepositoryPort
    business_repo: BusinessRepositoryPort

    async def execute(self, command: ListHolidaysCommand) -> Sequence[Holiday]:
        # Check business existence and ownership
        business = await get_owned_business(
            self.business_repo, command.business_id, command.owner_id
        )

        holidays = await self.holiday_repo.list_by_business(
            business.id, command.year, command.month
        )
        return holidays
