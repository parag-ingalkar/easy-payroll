from dataclasses import dataclass

from app.core.uow import AbstractUnitOfWork
from app.features.auth.application.commands import (
    CreateUserCommand,
    LoginUserCommand,
    LogoutUserCommand,
    RefreshTokenCommand,
)
from app.features.auth.application.ports import (
    PasswordHasherPort,
    TokenRepositoryPort,
    TokenServicePort,
    UserRepositoryPort,
)
from app.features.auth.domain.entities import RefreshToken, User
from app.features.auth.domain.exceptions import (
    AccessTokenExpiredError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
    UserAlreadyExists,
)
from app.features.auth.domain.value_objects import AccessToken, UserRole


@dataclass
class TokenResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class CreateUserUseCase:
    uow: AbstractUnitOfWork
    user_repo: UserRepositoryPort
    password_hasher: PasswordHasherPort

    async def execute(self, command: CreateUserCommand) -> User:
        async with self.uow:
            existing_user = await self.user_repo.get_by_email(command.email)
            if existing_user:
                raise UserAlreadyExists("Email already in use.")

            new_user = User.create(
                email=command.email,
                hashed_password=self.password_hasher.hash(command.password),
                name=command.name,
                roles=[UserRole.OWNER],
            )

            await self.user_repo.add(new_user)
            return new_user


@dataclass
class LoginUseCase:
    uow: AbstractUnitOfWork
    user_repo: UserRepositoryPort
    refresh_token_repo: TokenRepositoryPort
    password_hasher: PasswordHasherPort
    token_service: TokenServicePort

    async def execute(self, command: LoginUserCommand) -> TokenResponseDTO:
        async with self.uow:
            user = await self.user_repo.get_by_email(command.email)
            if not user or not self.password_hasher.verify(command.password, user.hashed_password):
                raise InvalidCredentialsError

            access_token_entity = AccessToken.create(user.id, user.roles)
            refresh_token_entity = RefreshToken.create(user.id)

            access_token = self.token_service.encode_access_token(access_token_entity)
            refresh_token = self.token_service.encode_refresh_token(refresh_token_entity)

            await self.refresh_token_repo.add(refresh_token_entity)

            return TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
            )


@dataclass
class RefreshTokenUseCase:
    uow: AbstractUnitOfWork
    user_repo: UserRepositoryPort
    refresh_token_repo: TokenRepositoryPort
    token_service: TokenServicePort

    async def execute(self, command: RefreshTokenCommand) -> TokenResponseDTO:
        claims = self.token_service.decode_refresh_token(command.refresh_token)
        if claims is None:
            raise InvalidTokenError("Invalid refresh token")

        async with self.uow:
            refresh_token = await self.refresh_token_repo.get_by_jti(claims.jti)
            if refresh_token is None or refresh_token.user_id != claims.user_id:
                raise InvalidTokenError("Invalid refresh token.")
            if not refresh_token.can_refresh():
                raise (
                    TokenRevokedError("Refresh token has been revoked.")
                    if refresh_token.revoked
                    else TokenExpiredError("Refresh token has expired.")
                )

            user = await self.user_repo.get_by_id(claims.user_id)
            if not user:
                raise InvalidTokenError("User associated with the refresh token not found.")

            refresh_token.revoke()
            await self.refresh_token_repo.revoke(refresh_token)

            new_access_token_entity = AccessToken.create(user.id, user.roles)
            new_refresh_token_entity = RefreshToken.create(user.id)

            new_access_token = self.token_service.encode_access_token(new_access_token_entity)
            new_refresh_token = self.token_service.encode_refresh_token(new_refresh_token_entity)

            await self.refresh_token_repo.add(new_refresh_token_entity)

            return TokenResponseDTO(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            )


@dataclass
class LogoutUseCase:
    uow: AbstractUnitOfWork
    refresh_token_repo: TokenRepositoryPort
    token_service: TokenServicePort

    async def execute(self, command: LogoutUserCommand) -> None:
        claims = self.token_service.decode_refresh_token(command.refresh_token)
        if claims is None:
            raise InvalidTokenError("Invalid refresh token")

        async with self.uow:
            refresh_token = await self.refresh_token_repo.get_by_jti(claims.jti)
            if refresh_token is not None:
                refresh_token.revoke()
                await self.refresh_token_repo.revoke(refresh_token)


@dataclass
class GetCurrentUserUseCase:
    user_repo: UserRepositoryPort
    token_service: TokenServicePort

    async def execute(self, access_token: str) -> User:
        claims = self.token_service.decode_access_token(access_token)
        if claims is None:
            raise InvalidAccessTokenError("Invalid access token")
        if claims.is_expired():
            raise AccessTokenExpiredError("Access token has expired")

        user = await self.user_repo.get_by_id(claims.user_id)
        if not user:
            raise InvalidTokenError("User not found.")

        return user
