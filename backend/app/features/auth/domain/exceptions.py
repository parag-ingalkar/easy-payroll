from app.core.exception_handler import ConflictError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    detail = "Invalid email or password provided"


class UserAlreadyExistsError(ConflictError):
    detail = "User with this email already exists"


class InvalidTokenError(UnauthorizedError):
    detail = "Invalid or expired token provided"


class InvalidAccessTokenError(UnauthorizedError):
    detail = "Invalid or expired access token provided"
    token_type = "access"
