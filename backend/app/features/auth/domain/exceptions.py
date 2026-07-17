"""Auth-domain exceptions."""

from app.core.exception_handler import ConflictError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    code = "invalid_credentials"
    detail = "Invalid email or password provided"


class UserAlreadyExistsError(ConflictError):
    code = "user_already_exists"
    detail = "User with this email already exists"

    def __init__(self, email: str) -> None:
        super().__init__(email=email)


class InvalidTokenError(UnauthorizedError):
    code = "invalid_token"
    detail = "Invalid or expired token provided"


class InvalidAccessTokenError(UnauthorizedError):
    code = "invalid_access_token"
    detail = "Invalid or expired access token provided"
    token_type = "access"
