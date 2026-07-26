"""Tests for platform integration connection model."""

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from security_system_database import Base
from security_system_database.models import PlatformIntegrationConnection


def _check_constraint_names(table_name: str) -> set[str]:
    table = Base.metadata.tables[table_name]

    return {
        constraint.name or ""
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }


def _index_names(table_name: str) -> set[str]:
    return {index.name for index in Base.metadata.tables[table_name].indexes}


def _index_by_name(table_name: str, index_name: str):
    matching_indexes = [
        index
        for index in Base.metadata.tables[table_name].indexes
        if index.name == index_name
    ]

    assert len(matching_indexes) == 1

    return matching_indexes[0]


def _foreign_key_by_column(table_name: str, column_name: str) -> ForeignKey:
    foreign_keys = list(Base.metadata.tables[table_name].c[column_name].foreign_keys)

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)

    return foreign_keys[0]


def _assert_no_raw_token_columns(table_name: str) -> None:
    raw_token_columns = {"access_token", "refresh_token", "token"}

    assert raw_token_columns.isdisjoint(Base.metadata.tables[table_name].columns.keys())


def test_platform_integration_connection_table_is_registered() -> None:
    assert PlatformIntegrationConnection.__tablename__ in Base.metadata.tables


def test_platform_integration_connection_columns_and_secret_storage() -> None:
    table = Base.metadata.tables["platform_integration_connections"]

    assert {
        "id",
        "provider_id",
        "connected_by_platform_user_id",
        "external_account_id",
        "external_account_email",
        "display_name",
        "access_token_encrypted",
        "refresh_token_encrypted",
        "token_expires_at",
        "scopes",
        "status",
        "last_checked_at",
        "last_error",
        "metadata",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert not table.c.provider_id.nullable
    assert isinstance(table.c.scopes.type, JSONB)
    assert isinstance(table.c.metadata.type, JSONB)
    assert table.c.scopes.server_default is not None
    assert table.c.metadata.server_default is not None
    assert table.c.status.server_default is not None
    _assert_no_raw_token_columns("platform_integration_connections")


def test_platform_integration_connection_constraints_and_indexes() -> None:
    table_name = "platform_integration_connections"

    assert (
        "ck_platform_integration_connections_status_valid"
        in _check_constraint_names(table_name)
    )
    assert "ix_platform_integration_connections_provider_id" in _index_names(table_name)
    assert "ix_platform_integration_connections_connected_by_user_id" in _index_names(
        table_name
    )
    assert "ix_platform_integration_connections_external_account_email" in _index_names(
        table_name
    )
    assert "ix_platform_integration_connections_status" in _index_names(table_name)
    assert "ix_platform_integration_connections_token_expires_at" in _index_names(
        table_name
    )

    provider_account_index = _index_by_name(
        table_name,
        "uq_platform_integration_connections_provider_external_account",
    )

    assert provider_account_index.unique
    assert tuple(provider_account_index.columns.keys()) == (
        "provider_id",
        "external_account_id",
    )
    assert str(provider_account_index.dialect_options["postgresql"]["where"]) == (
        "external_account_id IS NOT NULL"
    )


def test_platform_integration_connection_foreign_keys() -> None:
    provider_fk = _foreign_key_by_column(
        "platform_integration_connections",
        "provider_id",
    )
    connected_by_fk = _foreign_key_by_column(
        "platform_integration_connections",
        "connected_by_platform_user_id",
    )

    assert provider_fk.name == "fk_platform_integration_connections_provider_id"
    assert provider_fk.target_fullname == "platform_integration_providers.id"
    assert provider_fk.ondelete == "RESTRICT"
    assert (
        connected_by_fk.name
        == "fk_platform_integration_connections_connected_by_user_id"
    )
    assert connected_by_fk.target_fullname == "platform_users.id"
    assert connected_by_fk.ondelete == "SET NULL"
