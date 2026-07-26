"""Tests for platform configuration models."""

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint

from security_system_database import Base
from security_system_database.models import (
    PlatformIntegrationProvider,
    PlatformOAuthConfig,
    PlatformSetting,
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


def test_platform_configuration_tables_are_registered() -> None:
    assert PlatformSetting.__tablename__ in Base.metadata.tables
    assert PlatformIntegrationProvider.__tablename__ in Base.metadata.tables
    assert PlatformOAuthConfig.__tablename__ in Base.metadata.tables


def test_platform_configuration_tables_do_not_include_tenant_id() -> None:
    assert "tenant_id" not in Base.metadata.tables["platform_settings"].columns
    assert (
        "tenant_id"
        not in Base.metadata.tables["platform_integration_providers"].columns
    )
    assert "tenant_id" not in Base.metadata.tables["platform_oauth_configs"].columns


def test_platform_setting_columns_constraints_and_indexes() -> None:
    table = Base.metadata.tables["platform_settings"]

    assert {
        "id",
        "key",
        "value",
        "value_type",
        "description",
        "is_sensitive",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert ("key",) in _unique_constraint_columns("platform_settings")
    assert "ix_platform_settings_is_sensitive" in _index_names("platform_settings")
    assert "ix_platform_settings_value_type" in _index_names("platform_settings")
    assert "ck_platform_settings_key_lowercase" in _check_constraint_names(
        "platform_settings"
    )
    assert "ck_platform_settings_value_type_valid" in _check_constraint_names(
        "platform_settings"
    )


def test_platform_integration_provider_columns_constraints_and_indexes() -> None:
    table = Base.metadata.tables["platform_integration_providers"]

    assert {
        "id",
        "provider_key",
        "name",
        "category",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert ("provider_key",) in _unique_constraint_columns(
        "platform_integration_providers"
    )
    assert "ix_platform_integration_providers_category" in _index_names(
        "platform_integration_providers"
    )
    assert "ix_platform_integration_providers_status" in _index_names(
        "platform_integration_providers"
    )
    assert "ck_platform_integration_providers_provider_key_lowercase" in (
        _check_constraint_names("platform_integration_providers")
    )
    assert (
        "ck_platform_integration_providers_category_valid"
        in _check_constraint_names("platform_integration_providers")
    )
    assert "ck_platform_integration_providers_status_valid" in _check_constraint_names(
        "platform_integration_providers"
    )


def test_platform_oauth_config_columns_constraints_and_indexes() -> None:
    table = Base.metadata.tables["platform_oauth_configs"]

    assert {
        "id",
        "provider_id",
        "client_id",
        "client_secret_encrypted",
        "redirect_uri",
        "scopes",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert "client_secret" not in table.columns
    assert ("provider_id",) in _unique_constraint_columns("platform_oauth_configs")
    assert "ix_platform_oauth_configs_status" in _index_names("platform_oauth_configs")
    assert "ck_platform_oauth_configs_status_valid" in _check_constraint_names(
        "platform_oauth_configs"
    )


def test_platform_oauth_config_references_provider() -> None:
    foreign_keys = list(
        Base.metadata.tables["platform_oauth_configs"].c.provider_id.foreign_keys
    )

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)
    assert foreign_keys[0].name == "fk_platform_oauth_configs_provider_id"
    assert foreign_keys[0].target_fullname == "platform_integration_providers.id"
    assert foreign_keys[0].ondelete == "RESTRICT"
