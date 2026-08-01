from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://postgresuser:postgrespass@localhost/postgresdb"

    secret_key: SecretStr = SecretStr(
        "e264805baa45a3bb273f72768fcaf5adb9311f243addc48f25c4cfd3811130dd"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Comma-separated list of allowed frontend origins for CORS
    # Example: "http://localhost:3000,https://myapp.com,https://www.myapp.com"
    frontend_urls: str = "http://localhost:3000"
    
    @property
    def allowed_origins(self) -> list[str]:
        """Parse comma-separated frontend URLs into a list."""
        return [url.strip() for url in self.frontend_urls.split(",") if url.strip()]

    @field_validator("frontend_urls")
    @classmethod
    def validate_frontend_urls(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("frontend_urls cannot be empty")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
