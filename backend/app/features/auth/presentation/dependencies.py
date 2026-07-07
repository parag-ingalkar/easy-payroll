from fastapi import Depends

from app.features.auth.application.use_cases import (
    CreateUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
)
from app.features.auth.infrastructure.adapters import Argon2PasswordHasher, TokenService
from app.shared.infrastructure.sql_uow import SQLUnitOfWork
from app.shared.presentation.dependencies import get_uow


def get_password_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher()


def get_token_service() -> TokenService:
    return TokenService()


def get_create_user_use_case(
    uow: SQLUnitOfWork = Depends(get_uow),
    password_hasher: Argon2PasswordHasher = Depends(get_password_hasher),
):
    return CreateUserUseCase(uow=uow, password_hasher=password_hasher)


def get_login_use_case(
    uow: SQLUnitOfWork = Depends(get_uow),
    password_hasher: Argon2PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
):
    return LoginUseCase(uow=uow, password_hasher=password_hasher, token_service=token_service)


def get_refresh_token_use_case(
    uow: SQLUnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
):
    return RefreshTokenUseCase(uow=uow, token_service=token_service)


def get_logout_use_case(
    uow: SQLUnitOfWork = Depends(get_uow), token_service: TokenService = Depends(get_token_service)
):
    return LogoutUseCase(uow=uow, token_service=token_service)
