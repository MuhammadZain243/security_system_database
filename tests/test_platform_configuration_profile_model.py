"""Tests for general platform configuration model."""

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from security_system_database import Base
from security_system_database.models import PlatformConfiguration


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


def _assert_no_raw_secret_columns(table_name: str) -> None:
    raw_secret_columns = {
        "access_token",
        "api_key",
        "client_secret",
        "password",
        "refresh_token",
        "secret",
        "smtp_password",
        "token",
    }

    assert raw_secret_columns.isdisjoint(
        Base.metadata.tables[table_name].columns.keys()
    )


def test_platform_configuration_table_is_registered() -> None:
    assert PlatformConfiguration.__tablename__ in Base.metadata.tables


def test_platform_configuration_columns_and_json_storage() -> None:
    table = Base.metadata.tables["platform_configurations"]

    assert {
        "id",
        "config_type",
        "key",
        "name",
        "description",
        "integration_connection_id",
        "value",
        "status",
        "is_default",
        "is_sensitive",
        "metadata",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert not table.c.config_type.nullable
    assert not table.c.key.nullable
    assert not table.c.name.nullable
    assert isinstance(table.c.value.type, JSONB)
    assert isinstance(table.c.metadata.type, JSONB)
    assert table.c.value.server_default is not None
    assert table.c.metadata.server_default is not None
    assert table.c.status.server_default is not None
    assert table.c.is_default.server_default is not None
    assert table.c.is_sensitive.server_default is not None
    _assert_no_raw_secret_columns("platform_configurations")


def test_platform_configuration_constraints_and_indexes() -> None:
    table_name = "platform_configurations"

    assert "ck_platform_configurations_key_lowercase" in _check_constraint_names(
        table_name
    )
    assert "ck_platform_configurations_config_type_valid" in _check_constraint_names(
        table_name
    )
    assert "ck_platform_configurations_status_valid" in _check_constraint_names(
        table_name
    )
    assert "ix_platform_configurations_config_type" in _index_names(table_name)
    assert "ix_platform_configurations_integration_connection_id" in _index_names(
        table_name
    )
    assert "ix_platform_configurations_is_default" in _index_names(table_name)
    assert "ix_platform_configurations_is_sensitive" in _index_names(table_name)
    assert "ix_platform_configurations_key" in _index_names(table_name)
    assert "ix_platform_configurations_status" in _index_names(table_name)


def test_platform_configuration_partial_unique_indexes() -> None:
    type_key_index = _index_by_name(
        "platform_configurations",
        "uq_platform_configurations_type_key_active",
    )
    default_index = _index_by_name(
        "platform_configurations",
        "uq_platform_configurations_one_active_default_per_type",
    )

    assert type_key_index.unique
    assert tuple(type_key_index.columns.keys()) == ("config_type", "key")
    assert str(type_key_index.dialect_options["postgresql"]["where"]) == (
        "deleted_at IS NULL"
    )
    assert default_index.unique
    assert tuple(default_index.columns.keys()) == ("config_type",)
    assert str(default_index.dialect_options["postgresql"]["where"]) == (
        "is_default = true AND status = 'active' AND deleted_at IS NULL"
    )


def test_platform_configuration_integration_connection_foreign_key() -> None:
    integration_connection_fk = _foreign_key_by_column(
        "platform_configurations",
        "integration_connection_id",
    )

    assert (
        integration_connection_fk.name
        == "fk_platform_configurations_integration_connection_id"
    )
    assert (
        integration_connection_fk.target_fullname
        == "platform_integration_connections.id"
    )
    assert integration_connection_fk.ondelete == "RESTRICT"
