from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.application.ports import (
    PasswordHasherPort,
    TokenServicePort,
    UserRepositoryPort,
)
from app.features.auth.application.use_cases import (
    CreateUserUseCase,
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
)
from app.features.auth.domain.entities import User
from app.features.auth.infrastructure.adapters import Argon2PasswordHasher, TokenService
from app.features.auth.infrastructure.repositories import SQLUserRepository
from app.shared.application.uow_port import UnitOfWorkPort
from app.shared.presentation.dependencies import get_db, get_uow

bearer_scheme = HTTPBearer()


def get_password_hasher() -> PasswordHasherPort:
    return Argon2PasswordHasher()


def get_token_service() -> TokenServicePort:
    return TokenService()


def get_user_repository(db_session: AsyncSession = Depends(get_db)) -> UserRepositoryPort:
    return SQLUserRepository(db_session)


def get_current_user_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    token_service: TokenServicePort = Depends(get_token_service),
):
    return GetCurrentUserUseCase(user_repo=user_repo, token_service=token_service)


def get_create_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
):
    return CreateUserUseCase(uow=uow, password_hasher=password_hasher)


def get_login_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
):
    return LoginUseCase(uow=uow, password_hasher=password_hasher, token_service=token_service)


def get_refresh_token_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
):
    return RefreshTokenUseCase(uow=uow, token_service=token_service)


def get_logout_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
):
    return LogoutUseCase(uow=uow, token_service=token_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    use_case: "GetCurrentUserUseCase" = Depends(get_current_user_use_case),
) -> "User":
    access_token = credentials.credentials
    return await use_case.execute(access_token)
