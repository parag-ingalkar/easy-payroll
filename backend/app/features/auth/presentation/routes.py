from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.features.auth.application.commands import (
    CreateUserCommand,
    LoginUserCommand,
)
from app.features.auth.application.use_cases import CreateUserUseCase, LoginUseCase
from app.features.auth.domain.exceptions import InvalidCredentialsError
from app.features.auth.presentation.dependencies import (
    get_create_user_use_case,
    get_login_use_case,
)
from app.features.auth.presentation.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)

router = APIRouter(tags=["users"])


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
    request: LoginRequest,
    response: Response,
    login_use_case: LoginUseCase = Depends(get_login_use_case),
):
    command = LoginUserCommand(email=request.email, password=request.password)
    try:
        token_response = await login_use_case.execute(command)
    except InvalidCredentialsError as exc:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    settings = get_settings()
    max_age = settings.refresh_token_expire_days * 24 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=token_response.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=max_age,
        path="/",
    )

    return TokenResponse(
        access_token=token_response.access_token, expires_in=token_response.expires_in
    )
