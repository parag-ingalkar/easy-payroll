from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.features.auth.application.commands import (
    CreateUserCommand,
    LoginUserCommand,
)
from app.features.auth.application.ports import PasswordHasherPort, TokenServicePort
from app.features.auth.domain.entities import RefreshToken, User
from app.features.auth.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExists,
)
from app.features.auth.domain.value_objects import AccessToken, UserRole
from app.shared.application.uow_port import UnitOfWorkPort


@dataclass
class TokenResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass()
class CreateUserUseCase:
    uow: UnitOfWorkPort
    password_hasher: PasswordHasherPort

    async def execute(self, command: CreateUserCommand) -> User:
        async with self.uow as uow:
            existing_user = await uow.user_repo.get_by_email(command.email)
            if existing_user:
                raise UserAlreadyExists("Email already in use.")

            now_ = datetime.now(UTC)
            new_user = User(
                id=uuid4(),
                email=command.email.lower(),
                hashed_password=self.password_hasher.hash(command.password),
                name=command.name,
                created_at=now_,
                updated_at=now_,
                roles=[UserRole.OWNER],
            )

            await uow.user_repo.add(new_user)
            await uow.commit()
            return new_user


@dataclass()
class LoginUseCase:
    uow: "UnitOfWorkPort"
    password_hasher: "PasswordHasherPort"
    token_service: "TokenServicePort"

    async def execute(self, command: LoginUserCommand) -> TokenResponseDTO:
        async with self.uow as uow:
            user = await uow.user_repo.get_by_email(command.email)
            if not user or not self.password_hasher.verify(command.password, user.hashed_password):
                raise InvalidCredentialsError

            access_token_entity = AccessToken.create(user.id, user.roles)
            refresh_token_entity = RefreshToken.create(user.id)

            access_token = self.token_service.encode_access_token(access_token_entity)
            refresh_token = self.token_service.encode_refresh_token(refresh_token_entity)

            await uow.refresh_token_repo.add(refresh_token_entity)
            await uow.commit()

            return TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=access_token_entity.expires_in,
            )
