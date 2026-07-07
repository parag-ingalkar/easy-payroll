from fastapi import Request
from fastapi.responses import JSONResponse

from app.features.auth.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    MissingTokenError,
    TokenExpiredError,
    TokenRevokedError,
    UserAlreadyExists,
)


def register_auth_exception_handlers(app):
    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_exception_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "detail": {
                    "code": "invalid_credentials",
                    "message": "Invalid credentials.",
                }
            },
        )

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExists
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "detail": {
                    "code": "user_already_exists",
                    "message": "User already exists.",
                }
            },
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_exception_handler(
        request: Request, exc: InvalidTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "detail": {
                    "code": "invalid_token",
                    "message": "Invalid or expired refresh token.",
                }
            },
        )

    @app.exception_handler(TokenRevokedError)
    async def token_revoked_exception_handler(
        request: Request, exc: TokenRevokedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "detail": {
                    "code": "token_revoked",
                    "message": "Refresh token has been revoked.",
                }
            },
        )

    @app.exception_handler(TokenExpiredError)
    async def token_expired_exception_handler(
        request: Request, exc: TokenExpiredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "detail": {
                    "code": "token_expired",
                    "message": "Refresh token has expired.",
                }
            },
        )

    @app.exception_handler(MissingTokenError)
    async def missing_token_exception_handler(
        request: Request, exc: MissingTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "detail": {
                    "code": "missing_token",
                    "message": "No refresh token provided.",
                }
            },
        )
