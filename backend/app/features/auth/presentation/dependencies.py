from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.uow import SQLAlchemyUnitOfWork
from app.features.auth.application.use_cases import (
    CreateUserUseCase,
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
)
from app.features.auth.domain.entities import User
from app.features.auth.infrastructure.adapters import Argon2PasswordHasher, TokenService
from app.features.auth.infrastructure.repositories import SQLTokenRepository, SQLUserRepository

bearer_scheme = HTTPBearer()


def get_current_user_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    user_repo = SQLUserRepository(db_session)
    token_service = TokenService()
    return GetCurrentUserUseCase(user_repo=user_repo, token_service=token_service)


def get_create_user_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    user_repo = SQLUserRepository(db_session)
    password_hasher = Argon2PasswordHasher()
    return CreateUserUseCase(uow=uow, user_repo=user_repo, password_hasher=password_hasher)


def get_login_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    user_repo = SQLUserRepository(db_session)
    refresh_token_repo = SQLTokenRepository(db_session)
    password_hasher = Argon2PasswordHasher()
    token_service = TokenService()
    return LoginUseCase(
        uow=uow,
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_refresh_token_use_case(db_session: AsyncSession = Depends(get_db)):
    uow = SQLAlchemyUnitOfWork(db_session)
    user_repo = SQLUserRepository(db_session)
    refresh_token_repo = SQLTokenRepository(db_session)
    token_service = TokenService()
    return RefreshTokenUseCase(
        uow=uow,
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        token_service=token_service,
    )


def get_logout_use_case(
    db_session: AsyncSession = Depends(get_db),
):
    uow = SQLAlchemyUnitOfWork(db_session)
    refresh_token_repo = SQLTokenRepository(db_session)
    token_service = TokenService()
    return LogoutUseCase(
        uow=uow, refresh_token_repo=refresh_token_repo, token_service=token_service
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    use_case: "GetCurrentUserUseCase" = Depends(get_current_user_use_case),
) -> "User":
    access_token = credentials.credentials
    return await use_case.execute(access_token)
