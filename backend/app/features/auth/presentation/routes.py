from fastapi import APIRouter, Depends, Request, Response, status

from app.core.config import get_settings
from app.features.auth.application.commands import (
    CreateUserCommand,
    LoginUserCommand,
    LogoutUserCommand,
    RefreshTokenCommand,
)
from app.features.auth.application.use_cases import (
    CreateUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
)
from app.features.auth.domain.entities import User
from app.features.auth.domain.exceptions import (
    InvalidTokenError,
    MissingTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from app.features.auth.presentation.dependencies import (
    get_create_user_use_case,
    get_current_user,
    get_login_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
)
from app.features.auth.presentation.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)


def _set_refresh_token_cookie(response: Response, refresh_token: str, *, secure: bool) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=get_settings().refresh_token_expire_days * 24 * 60 * 60,
        path="/api/auth",
    )


def _clear_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth",
    )


router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create_request: UserCreateRequest,
    create_user_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    command = CreateUserCommand(
        email=user_create_request.email,
        password=user_create_request.password,
        name=user_create_request.name,
    )
    new_user = await create_user_use_case.execute(command)
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        roles=new_user.roles,
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_request: LoginRequest,
    response: Response,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
):
    command = LoginUserCommand(
        email=login_request.email,
        password=login_request.password,
    )

    token_response = await login_use_case.execute(command)

    _set_refresh_token_cookie(
        response,
        token_response.refresh_token,
        secure=request.url.scheme == "https",
    )
    return TokenResponse(
        access_token=token_response.access_token,
        refresh_token=token_response.refresh_token,
    )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    cookie_refresh_token = request.cookies.get("refresh_token")
    refresh_token = cookie_refresh_token or (body.refresh_token if body else None)
    if not refresh_token:
        raise MissingTokenError("No refresh token provided.")
    command = RefreshTokenCommand(refresh_token=refresh_token)

    try:
        token_response = await use_case.execute(command)
    except (InvalidTokenError, TokenRevokedError, TokenExpiredError):
        _clear_refresh_token_cookie(response)
        raise

    _set_refresh_token_cookie(
        response,
        token_response.refresh_token,
        secure=request.url.scheme == "https",
    )

    return TokenResponse(
        access_token=token_response.access_token,
        refresh_token=token_response.refresh_token,
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
):
    cookie_refresh_token = request.cookies.get("refresh_token")
    refresh_token = cookie_refresh_token or (body.refresh_token if body else None)
    if not refresh_token:
        _clear_refresh_token_cookie(response)
        return None

    try:
        command = LogoutUserCommand(refresh_token=refresh_token)
        await use_case.execute(command)
    except (InvalidTokenError, TokenRevokedError, TokenExpiredError):
        pass

    _clear_refresh_token_cookie(response)
    return None


@router.get("/users/me", response_model=UserResponse)
async def current_user(
    current_user: "User" = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        roles=current_user.roles,
    )
