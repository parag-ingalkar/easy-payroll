from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUserCommand:
    email: str
    password: str
    name: str


@dataclass(frozen=True)
class LoginUserCommand:
    email: str
    password: str


@dataclass(frozen=True)
class RefreshTokenCommand:
    refresh_token: str


@dataclass(frozen=True)
class LogoutUserCommand:
    refresh_token: str
