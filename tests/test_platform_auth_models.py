"""Tests for platform authentication session and token models."""

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from security_system_database import Base
from security_system_database.models import (
    PlatformAuthEvent,
    PlatformEmailVerificationToken,
    PlatformPasswordResetToken,
    PlatformRefreshToken,
    PlatformUserSession,
)


def _unique_constraint_columns(table_name: str) -> set[tuple[str, ...]]:
    table = Base.metadata.tables[table_name]

    return {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def _check_constraint_names(table_name: str) -> set[str]:
    table = Base.metadata.tables[table_name]

    return {
        constraint.name or ""
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }


def _index_names(table_name: str) -> set[str]:
    return {index.name for index in Base.metadata.tables[table_name].indexes}


def _foreign_key_by_column(table_name: str, column_name: str) -> ForeignKey:
    foreign_keys = list(Base.metadata.tables[table_name].c[column_name].foreign_keys)

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)

    return foreign_keys[0]


def _assert_no_raw_token_columns(table_name: str) -> None:
    raw_token_columns = {
        "token",
        "session_token",
        "refresh_token",
        "password_reset_token",
        "email_verification_token",
    }

    assert raw_token_columns.isdisjoint(Base.metadata.tables[table_name].columns.keys())


def test_platform_auth_tables_are_registered() -> None:
    assert PlatformUserSession.__tablename__ in Base.metadata.tables
    assert PlatformRefreshToken.__tablename__ in Base.metadata.tables
    assert PlatformPasswordResetToken.__tablename__ in Base.metadata.tables
    assert PlatformEmailVerificationToken.__tablename__ in Base.metadata.tables
    assert PlatformAuthEvent.__tablename__ in Base.metadata.tables


def test_platform_user_session_columns_constraints_indexes_and_foreign_key() -> None:
    table = Base.metadata.tables["platform_user_sessions"]

    assert {
        "id",
        "platform_user_id",
        "session_token_hash",
        "ip_address",
        "user_agent",
        "status",
        "expires_at",
        "revoked_at",
        "last_seen_at",
        "created_at",
        "updated_at",
    }.issubset(table.columns.keys())
    assert ("session_token_hash",) in _unique_constraint_columns(
        "platform_user_sessions"
    )
    assert "ck_platform_user_sessions_status_valid" in _check_constraint_names(
        "platform_user_sessions"
    )
    assert "ix_platform_user_sessions_platform_user_id" in _index_names(
        "platform_user_sessions"
    )
    assert "ix_platform_user_sessions_status" in _index_names("platform_user_sessions")
    assert "ix_platform_user_sessions_expires_at" in _index_names(
        "platform_user_sessions"
    )
    assert table.c.status.server_default is not None
    _assert_no_raw_token_columns("platform_user_sessions")

    platform_user_fk = _foreign_key_by_column(
        "platform_user_sessions",
        "platform_user_id",
    )

    assert platform_user_fk.name == "fk_platform_user_sessions_platform_user_id"
    assert platform_user_fk.target_fullname == "platform_users.id"
    assert platform_user_fk.ondelete == "CASCADE"


def test_platform_refresh_token_columns_constraints_indexes_and_foreign_keys() -> None:
    table = Base.metadata.tables["platform_refresh_tokens"]

    assert {
        "id",
        "platform_user_id",
        "session_id",
        "token_hash",
        "status",
        "expires_at",
        "revoked_at",
        "rotated_at",
        "created_at",
        "updated_at",
    }.issubset(table.columns.keys())
    assert ("token_hash",) in _unique_constraint_columns("platform_refresh_tokens")
    assert "ck_platform_refresh_tokens_status_valid" in _check_constraint_names(
        "platform_refresh_tokens"
    )
    assert "ix_platform_refresh_tokens_platform_user_id" in _index_names(
        "platform_refresh_tokens"
    )
    assert "ix_platform_refresh_tokens_session_id" in _index_names(
        "platform_refresh_tokens"
    )
    assert "ix_platform_refresh_tokens_status" in _index_names(
        "platform_refresh_tokens"
    )
    assert "ix_platform_refresh_tokens_expires_at" in _index_names(
        "platform_refresh_tokens"
    )
    assert table.c.status.server_default is not None
    _assert_no_raw_token_columns("platform_refresh_tokens")

    platform_user_fk = _foreign_key_by_column(
        "platform_refresh_tokens",
        "platform_user_id",
    )
    session_fk = _foreign_key_by_column("platform_refresh_tokens", "session_id")

    assert platform_user_fk.name == "fk_platform_refresh_tokens_platform_user_id"
    assert platform_user_fk.target_fullname == "platform_users.id"
    assert platform_user_fk.ondelete == "CASCADE"
    assert session_fk.name == "fk_platform_refresh_tokens_session_id"
    assert session_fk.target_fullname == "platform_user_sessions.id"
    assert session_fk.ondelete == "CASCADE"


def test_platform_password_reset_token_columns_constraints_indexes_and_foreign_key() -> (
    None
):
    table = Base.metadata.tables["platform_password_reset_tokens"]

    assert {
        "id",
        "platform_user_id",
        "token_hash",
        "expires_at",
        "used_at",
        "created_at",
    }.issubset(table.columns.keys())
    assert ("token_hash",) in _unique_constraint_columns(
        "platform_password_reset_tokens"
    )
    assert "ix_platform_password_reset_tokens_platform_user_id" in _index_names(
        "platform_password_reset_tokens"
    )
    assert "ix_platform_password_reset_tokens_expires_at" in _index_names(
        "platform_password_reset_tokens"
    )
    assert table.c.created_at.server_default is not None
    _assert_no_raw_token_columns("platform_password_reset_tokens")

    platform_user_fk = _foreign_key_by_column(
        "platform_password_reset_tokens",
        "platform_user_id",
    )

    assert platform_user_fk.name == "fk_platform_password_reset_tokens_platform_user_id"
    assert platform_user_fk.target_fullname == "platform_users.id"
    assert platform_user_fk.ondelete == "CASCADE"


def test_platform_email_verification_token_columns_constraints_indexes_and_foreign_key() -> (
    None
):
    table = Base.metadata.tables["platform_email_verification_tokens"]

    assert {
        "id",
        "platform_user_id",
        "token_hash",
        "expires_at",
        "used_at",
        "created_at",
    }.issubset(table.columns.keys())
    assert ("token_hash",) in _unique_constraint_columns(
        "platform_email_verification_tokens"
    )
    assert "ix_platform_email_verification_tokens_platform_user_id" in _index_names(
        "platform_email_verification_tokens"
    )
    assert "ix_platform_email_verification_tokens_expires_at" in _index_names(
        "platform_email_verification_tokens"
    )
    assert table.c.created_at.server_default is not None
    _assert_no_raw_token_columns("platform_email_verification_tokens")

    platform_user_fk = _foreign_key_by_column(
        "platform_email_verification_tokens",
        "platform_user_id",
    )

    assert (
        platform_user_fk.name
        == "fk_platform_email_verification_tokens_platform_user_id"
    )
    assert platform_user_fk.target_fullname == "platform_users.id"
    assert platform_user_fk.ondelete == "CASCADE"


def test_platform_auth_event_columns_constraints_indexes_and_foreign_key() -> None:
    table = Base.metadata.tables["platform_auth_events"]

    assert {
        "id",
        "platform_user_id",
        "event_type",
        "ip_address",
        "user_agent",
        "metadata",
        "created_at",
    }.issubset(table.columns.keys())
    assert "ck_platform_auth_events_event_type_valid" in _check_constraint_names(
        "platform_auth_events"
    )
    assert "ix_platform_auth_events_platform_user_id" in _index_names(
        "platform_auth_events"
    )
    assert "ix_platform_auth_events_event_type" in _index_names("platform_auth_events")
    assert "ix_platform_auth_events_created_at" in _index_names("platform_auth_events")
    assert isinstance(table.c.metadata.type, JSONB)
    assert table.c.metadata.server_default is not None
    assert table.c.created_at.server_default is not None
    _assert_no_raw_token_columns("platform_auth_events")

    platform_user_fk = _foreign_key_by_column(
        "platform_auth_events",
        "platform_user_id",
    )

    assert platform_user_fk.name == "fk_platform_auth_events_platform_user_id"
    assert platform_user_fk.target_fullname == "platform_users.id"
    assert platform_user_fk.ondelete == "SET NULL"
