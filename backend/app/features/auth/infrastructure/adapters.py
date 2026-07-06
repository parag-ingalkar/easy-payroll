import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.features.auth.application.ports import PasswordHasherPort, TokenServicePort
from app.features.auth.domain.entities import RefreshToken
from app.features.auth.domain.value_objects import AccessToken


class Argon2PasswordHasher(PasswordHasherPort):
    def __init__(self):
        self.hasher = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self.hasher.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self.hasher.verify(password, hashed_password)


class TokenService(TokenServicePort):
    def encode_access_token(self, access_token: AccessToken) -> str:
        payload = {
            "sub": str(access_token.user_id),
            "roles": [role.value for role in access_token.roles],
            "exp": access_token.expires_at.timestamp(),
            "type": "access",
            "iat": access_token.created_at.timestamp(),
        }
        return jwt.encode(
            payload,
            get_settings().secret_key.get_secret_value(),
            get_settings().algorithm,
        )

    def encode_refresh_token(self, refresh_token: RefreshToken) -> str:
        payload = {
            "sub": str(refresh_token.user_id),
            "jti": refresh_token.jti,
            "exp": refresh_token.expires_at.timestamp(),
            "type": "refresh",
            "iat": refresh_token.created_at.timestamp(),
        }
        return jwt.encode(
            payload,
            get_settings().secret_key.get_secret_value(),
            get_settings().algorithm,
        )
