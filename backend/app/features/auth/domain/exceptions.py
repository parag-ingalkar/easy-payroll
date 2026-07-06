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

    def __init__(self, message="Invalid or expired token."):
        self.message = message
        super().__init__(self.message)


class InsufficientPermissionsError(AuthError):
    """Raised when a user does not have the required permissions."""

    def __init__(self, message="Insufficient permissions."):
        self.message = message
        super().__init__(self.message)
