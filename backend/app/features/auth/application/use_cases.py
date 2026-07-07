from dataclasses import dataclass

from app.features.auth.application.commands import (
    CreateUserCommand,
    LoginUserCommand,
    LogoutUserCommand,
    RefreshTokenCommand,
)
from app.features.auth.application.ports import PasswordHasherPort, TokenServicePort
from app.features.auth.domain.entities import RefreshToken, User
from app.features.auth.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
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

            new_user = User.create(
                email=command.email,
                hashed_password=self.password_hasher.hash(command.password),
                name=command.name,
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


@dataclass()
class RefreshTokenUseCase:
    uow: "UnitOfWorkPort"
    token_service: "TokenServicePort"

    async def execute(self, command: RefreshTokenCommand) -> TokenResponseDTO:
        claims = self.token_service.decode_refresh_token(command.refresh_token)
        print(f"Decoded claims: {claims}")  # Debugging line
        print(f"Refresh token: {command.refresh_token}")  # Debugging line
        if claims is None:
            raise InvalidTokenError("Invalid refresh token")

        async with self.uow as uow:
            refresh_token = await uow.refresh_token_repo.get_by_jti(claims.jti)
            if refresh_token is None or refresh_token.user_id != claims.user_id:
                raise InvalidTokenError("Invalid refresh token.")
            if not refresh_token.can_refresh():
                raise (
                    TokenRevokedError("Refresh token has been revoked.")
                    if refresh_token.revoked
                    else TokenExpiredError("Refresh token has expired.")
                )

            user = await uow.user_repo.get_by_id(claims.user_id)
            if not user:
                raise InvalidTokenError("User associated with the refresh token not found.")

            refresh_token.revoke()
            await uow.refresh_token_repo.revoke(refresh_token)

            new_access_token_entity = AccessToken.create(user.id, user.roles)
            new_refresh_token_entity = RefreshToken.create(user.id)

            new_access_token = self.token_service.encode_access_token(new_access_token_entity)
            new_refresh_token = self.token_service.encode_refresh_token(new_refresh_token_entity)

            await uow.refresh_token_repo.add(new_refresh_token_entity)
            await uow.commit()

            return TokenResponseDTO(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=new_access_token_entity.expires_in,
            )


@dataclass()
class LogoutUseCase:
    uow: "UnitOfWorkPort"
    token_service: "TokenServicePort"

    async def execute(self, command: LogoutUserCommand) -> None:
        claims = self.token_service.decode_refresh_token(command.refresh_token)
        if claims is None:
            raise InvalidTokenError("Invalid refresh token")

        async with self.uow as uow:
            refresh_token = await uow.refresh_token_repo.get_by_jti(claims.jti)
            if refresh_token is not None:
                print(f"Revoking refresh token: {refresh_token}")  # Debugging line
                refresh_token.revoke()
                await uow.refresh_token_repo.revoke(refresh_token)
                await uow.commit()
