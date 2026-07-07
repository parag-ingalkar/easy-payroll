class AuthError(Exception):
    """Base class for authentication errors."""

    pass


class InvalidCredentialsError(AuthError):
    """Raised when the provided credentials are invalid."""

    def __init__(self, message="Invalid credentials provided."):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExists(AuthError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message="User already exists."):
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(AuthError):
    """Raised when the provided token is invalid or expired."""

    def __init__(self, message="Invalid or expired refresh token."):
        self.message = message
        super().__init__(self.message)


class InvalidAccessTokenError(AuthError):
    """Raised when the provided token is invalid or expired."""

    def __init__(self, message="Invalid or expired access token."):
        self.message = message
        super().__init__(self.message)


class TokenRevokedError(AuthError):
    """Raised when the provided token has been revoked."""

    def __init__(self, message="Refresh token has been revoked."):
        self.message = message
        super().__init__(self.message)


class TokenExpiredError(AuthError):
    """Raised when the provided token has expired."""

    def __init__(self, message="Refresh token has expired."):
        self.message = message
        super().__init__(self.message)


class AccessTokenExpiredError(AuthError):
    """Raised when the provided token has expired."""

    def __init__(self, message="Access token has expired."):
        self.message = message
        super().__init__(self.message)


class MissingTokenError(AuthError):
    """Raised when the provided token has expired."""

    def __init__(self, message="Refresh token has expired."):
        self.message = message
        super().__init__(self.message)
