from typing import Protocol
from uuid import UUID

from app.features.auth.domain.entities import RefreshToken, User
from app.features.auth.domain.value_objects import AccessToken


class PasswordHasherPort(Protocol):
    def hash(self, password: str) -> str:
        """Hashes the given password and returns the hashed value."""
        ...

    def verify(self, password: str, hashed_password: str) -> bool:
        """Verifies if the given password matches the hashed password."""
        ...


class TokenServicePort(Protocol):
    def encode_access_token(self, access_token: AccessToken) -> str:
        """Creates an access token for the given user details."""
        ...

    def encode_refresh_token(self, refresh_token: RefreshToken) -> str:
        """Creates a refresh token and returns it along with its JTI and expiration datetime."""
        ...


class UserRepositoryPort(Protocol):
    async def get_by_email(self, email: str) -> User | None:
        """Fetches a user by their email address."""
        ...

    async def get_by_id(self, id: "UUID") -> User | None:
        """Fetches a user by their id."""
        ...

    async def add(self, user: User) -> None:
        """Adds a new user to the repository."""
        ...


class TokenRepositoryPort(Protocol):
    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        """Fetches a refresh token by its JTI."""
        ...

    async def add(self, refresh_token: RefreshToken) -> None:
        """Adds a new refresh token to the repository."""
        ...

    async def revoke(self, refresh_token: RefreshToken) -> None:
        """Marks a refresh token as revoked."""
        ...
