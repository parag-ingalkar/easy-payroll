from collections.abc import Sequence
from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.business.application.ports import BusinessRepositoryPort
from app.features.business.domain.exceptions import BusinessNotOwnedError
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
            business = await self.business_repo.get_by_id_and_owner_id(
                command.business_id, command.owner_id
            )
            if not business:
                raise BusinessNotOwnedError

            # Check for duplicate holiday
            existing_holiday = await self.holiday_repo.get_by_business_id_and_date(
                command.business_id, command.holiday_date
            )
            if existing_holiday:
                raise DuplicateHolidayError

            holiday = Holiday.create(
                business_id=command.business_id,
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
            business = await self.business_repo.get_by_id_and_owner_id(
                command.business_id, command.owner_id
            )
            if not business:
                raise BusinessNotOwnedError

            # Check if the holiday exists
            holiday = await self.holiday_repo.get_by_business_id_and_date(
                command.business_id, command.holiday_date
            )
            if not holiday:
                raise HolidayNotFoundError

            await self.holiday_repo.delete(holiday)


@dataclass
class GetHolidayUseCase:
    holiday_repo: HolidaysRepositoryPort
    business_repo: BusinessRepositoryPort

    async def execute(self, command: GetHolidayCommand) -> Holiday:
        # Check business existence and ownership
        business = await self.business_repo.get_by_id_and_owner_id(
            command.business_id, command.owner_id
        )
        if not business:
            raise BusinessNotOwnedError

        holiday = await self.holiday_repo.get_by_business_id_and_date(
            command.business_id, command.holiday_date
        )
        if not holiday:
            raise HolidayNotFoundError

        return holiday


@dataclass
class ListHolidaysUseCase:
    holiday_repo: HolidaysRepositoryPort
    business_repo: BusinessRepositoryPort

    async def execute(self, command: ListHolidaysCommand) -> Sequence[Holiday]:
        # Check business existence and ownership
        business = await self.business_repo.get_by_id_and_owner_id(
            command.business_id, command.owner_id
        )
        if not business:
            raise BusinessNotOwnedError

        holidays = await self.holiday_repo.list_by_business(
            command.business_id, command.year, command.month
        )
        return holidays
