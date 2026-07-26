"""Tests for the platform Super Admin bootstrap seed."""

from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from security_system_database.seeds.platform_super_admin import (
    PlatformSuperAdminSettings,
    hash_password,
    normalize_email,
    seed_platform_super_admin,
)


def test_platform_super_admin_settings_read_email_and_password() -> None:
    settings = PlatformSuperAdminSettings(
        _env_file=None,
        email="zainm2432003@gmail.com",
        password="local-strong-password",
    )

    assert settings.email == "zainm2432003@gmail.com"
    assert settings.password.get_secret_value() == "local-strong-password"


def test_platform_super_admin_settings_require_email() -> None:
    with pytest.raises(ValidationError):
        PlatformSuperAdminSettings(
            _env_file=None,
            password="local-strong-password",
        )


def test_platform_super_admin_settings_require_password() -> None:
    with pytest.raises(ValidationError):
        PlatformSuperAdminSettings(
            _env_file=None,
            email="zainm2432003@gmail.com",
        )


def test_normalize_email_lowercases_and_strips_value() -> None:
    assert normalize_email("  ZainM2432003@GMAIL.COM  ") == "zainm2432003@gmail.com"


def test_normalize_email_rejects_invalid_email() -> None:
    with pytest.raises(ValueError, match="valid email"):
        normalize_email("not-an-email")


def test_hash_password_does_not_store_plaintext_password() -> None:
    password = "local-strong-password"
    password_hash = hash_password(password)

    assert password not in password_hash
    assert password_hash.startswith("pbkdf2_sha256$")
    assert len(password_hash.split("$")) == 4


def test_hash_password_uses_random_salt() -> None:
    password = "local-strong-password"

    assert hash_password(password) != hash_password(password)


def _build_seed_test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE platform_users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    is_super_admin BOOLEAN NOT NULL,
                    email_verified_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE platform_roles (
                    id TEXT PRIMARY KEY,
                    slug TEXT NOT NULL UNIQUE
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE platform_user_roles (
                    id TEXT PRIMARY KEY,
                    platform_user_id TEXT NOT NULL,
                    platform_role_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (platform_user_id, platform_role_id)
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO platform_roles (id, slug)
                VALUES (:id, 'super-admin')
                """
            ),
            {"id": str(uuid4())},
        )

    return engine


def test_seed_platform_super_admin_creates_user_and_assigns_role() -> None:
    engine = _build_seed_test_engine()
    settings = PlatformSuperAdminSettings(
        _env_file=None,
        email="ZainM2432003@GMAIL.COM",
        password="local-strong-password",
    )

    result = seed_platform_super_admin(settings=settings, engine=engine)

    with engine.begin() as connection:
        user_count = connection.execute(
            text("SELECT COUNT(*) FROM platform_users")
        ).scalar_one()
        role_count = connection.execute(
            text("SELECT COUNT(*) FROM platform_user_roles")
        ).scalar_one()
        user = connection.execute(
            text(
                """
                SELECT email, password_hash, status, is_super_admin
                FROM platform_users
                """
            )
        ).one()

    assert result.created is True
    assert result.updated_existing_user is False
    assert result.role_assigned is True
    assert user_count == 1
    assert role_count == 1
    assert user.email == "zainm2432003@gmail.com"
    assert user.password_hash != "local-strong-password"
    assert user.status == "active"
    assert bool(user.is_super_admin) is True


def test_seed_platform_super_admin_is_idempotent() -> None:
    engine = _build_seed_test_engine()
    settings = PlatformSuperAdminSettings(
        _env_file=None,
        email="zainm2432003@gmail.com",
        password="local-strong-password",
    )

    first_result = seed_platform_super_admin(settings=settings, engine=engine)
    second_result = seed_platform_super_admin(settings=settings, engine=engine)

    with engine.begin() as connection:
        user_count = connection.execute(
            text("SELECT COUNT(*) FROM platform_users")
        ).scalar_one()
        role_count = connection.execute(
            text("SELECT COUNT(*) FROM platform_user_roles")
        ).scalar_one()

    assert first_result.created is True
    assert second_result.created is False
    assert second_result.updated_existing_user is True
    assert user_count == 1
    assert role_count == 1


def test_seed_platform_super_admin_rejects_existing_non_super_admin() -> None:
    engine = _build_seed_test_engine()
    settings = PlatformSuperAdminSettings(
        _env_file=None,
        email="zainm2432003@gmail.com",
        password="local-strong-password",
    )

    with engine.begin() as connection:
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
                    'zainm2432003@gmail.com',
                    'existing-hash',
                    'active',
                    false,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            {"id": str(uuid4())},
        )

    with pytest.raises(ValueError, match="not a Super Admin"):
        seed_platform_super_admin(settings=settings, engine=engine)
