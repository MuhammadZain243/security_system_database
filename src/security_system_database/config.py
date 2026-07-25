"""Database configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

SSLMode = Literal[
    "disable",
    "allow",
    "prefer",
    "require",
    "verify-ca",
    "verify-full",
]


class DatabaseSettings(BaseSettings):
    """Validated PostgreSQL and SQLAlchemy configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = "security_system"
    user: str = "security_system"
    password: SecretStr

    ssl_mode: SSLMode = "prefer"
    echo: bool = False

    pool_size: int = Field(default=10, ge=1)
    max_overflow: int = Field(default=20, ge=0)
    pool_timeout_seconds: int = Field(default=30, ge=1)
    pool_recycle_seconds: int = Field(default=1800, ge=1)
    connect_timeout_seconds: int = Field(default=10, ge=1)

    @property
    def sqlalchemy_url(self) -> URL:
        """Build the SQLAlchemy PostgreSQL connection URL."""

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.name,
            query={"sslmode": self.ssl_mode},
        )


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Return one cached settings object for the current process."""

    return DatabaseSettings()  # type: ignore[call-arg]
