"""Bootstrap seed for the initial platform Super Admin user."""

from base64 import urlsafe_b64encode
from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from secrets import token_bytes
from uuid import UUID, uuid4

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, text

from security_system_database import build_engine

PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 600_000
SALT_BYTES = 16


class PlatformSuperAdminSettings(BaseSettings):
    """Platform Super Admin seed settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="PLATFORM_SUPER_ADMIN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    email: str = Field(min_length=3)
    password: SecretStr = Field(min_length=12)


@dataclass(frozen=True)
class PlatformSuperAdminSeedResult:
    """Result returned by the platform Super Admin seed."""

    email: str
    created: bool
    updated_existing_user: bool
    role_assigned: bool


def normalize_email(email: str) -> str:
    """Normalize a platform Super Admin email address."""

    normalized_email = email.strip().lower()
    if "@" not in normalized_email:
        raise ValueError("PLATFORM_SUPER_ADMIN_EMAIL must be a valid email address.")

    return normalized_email


def hash_password(password: str) -> str:
    """Hash a password for bootstrap storage."""

    salt = token_bytes(SALT_BYTES)
    digest = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )

    encoded_salt = urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    encoded_digest = urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    return (
        f"{PASSWORD_HASH_ALGORITHM}"
        f"${PASSWORD_HASH_ITERATIONS}"
        f"${encoded_salt}"
        f"${encoded_digest}"
    )


def get_platform_super_admin_settings() -> PlatformSuperAdminSettings:
    """Load platform Super Admin seed settings from the environment."""

    return PlatformSuperAdminSettings()  # type: ignore[call-arg]


def _database_uuid(value: UUID, dialect_name: str) -> UUID | str:
    """Return a UUID value in a form accepted by the active database driver."""

    if dialect_name == "sqlite":
        return str(value)

    return value


def seed_platform_super_admin(
    settings: PlatformSuperAdminSettings | None = None,
    engine: Engine | None = None,
) -> PlatformSuperAdminSeedResult:
    """Create the initial platform Super Admin account if it does not exist."""

    resolved_settings = settings or get_platform_super_admin_settings()
    email = normalize_email(resolved_settings.email)
    password = resolved_settings.password.get_secret_value()

    if not password.strip():
        raise ValueError("PLATFORM_SUPER_ADMIN_PASSWORD must not be empty.")

    resolved_engine = engine or build_engine()
    should_dispose_engine = engine is None

    try:
        with resolved_engine.begin() as connection:
            dialect_name = connection.dialect.name
            existing_user = connection.execute(
                text(
                    """
                    SELECT id, is_super_admin
                    FROM platform_users
                    WHERE email = :email
                    """
                ),
                {"email": email},
            ).one_or_none()

            updated_existing_user = False

            if existing_user is None:
                created = True
                platform_user_id = _database_uuid(uuid4(), dialect_name)
                connection.execute(
                    text(
                        """
                        INSERT INTO platform_users (
                            id,
                            email,
                            password_hash,
                            status,
                            is_super_admin,
                            email_verified_at,
                            created_at,
                            updated_at
                        )
                        VALUES (
                            :id,
                            :email,
                            :password_hash,
                            'active',
                            true,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                        """
                    ),
                    {
                        "id": platform_user_id,
                        "email": email,
                        "password_hash": hash_password(password),
                    },
                )
            else:
                created = False
                platform_user_id = existing_user.id
                if not existing_user.is_super_admin:
                    raise ValueError(
                        "A platform user with PLATFORM_SUPER_ADMIN_EMAIL already "
                        "exists but is not a Super Admin. Review this account "
                        "manually before running the bootstrap seed again."
                    )

                connection.execute(
                    text(
                        """
                        UPDATE platform_users
                        SET
                            status = 'active',
                            email_verified_at = COALESCE(
                                email_verified_at,
                                CURRENT_TIMESTAMP
                            ),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                        """
                    ),
                    {"id": platform_user_id},
                )
                updated_existing_user = True

            super_admin_role_id = connection.execute(
                text(
                    """
                    SELECT id
                    FROM platform_roles
                    WHERE slug = 'super-admin'
                    """
                )
            ).scalar_one_or_none()

            role_assigned = super_admin_role_id is not None

            if role_assigned:
                connection.execute(
                    text(
                        """
                        INSERT INTO platform_user_roles (
                            id,
                            platform_user_id,
                            platform_role_id,
                            created_at
                        )
                        VALUES (
                            :id,
                            :platform_user_id,
                            :platform_role_id,
                            CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (
                            platform_user_id,
                            platform_role_id
                        ) DO NOTHING
                        """
                    ),
                    {
                        "id": _database_uuid(uuid4(), dialect_name),
                        "platform_user_id": platform_user_id,
                        "platform_role_id": super_admin_role_id,
                    },
                )

            return PlatformSuperAdminSeedResult(
                email=email,
                created=created,
                updated_existing_user=updated_existing_user,
                role_assigned=role_assigned,
            )
    finally:
        if should_dispose_engine:
            resolved_engine.dispose()


def main() -> None:
    """CLI entrypoint for the platform Super Admin seed."""

    result = seed_platform_super_admin()

    if result.created:
        print("Platform Super Admin created successfully.")
    elif result.updated_existing_user:
        print("Existing Platform Super Admin refreshed.")
    else:
        print("Platform Super Admin already exists. Skipping.")

    if result.role_assigned:
        print("Super Admin role assigned.")
    else:
        print("Super Admin role not found. Skipping role assignment.")


if __name__ == "__main__":
    main()
