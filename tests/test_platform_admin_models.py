"""Tests for platform administrator and RBAC models."""

from sqlalchemy import UniqueConstraint

from security_system_database import Base
from security_system_database.models import (
    PlatformPermission,
    PlatformRole,
    PlatformRolePermission,
    PlatformUser,
    PlatformUserRole,
)


def _unique_constraint_columns(table_name: str) -> set[tuple[str, ...]]:
    table = Base.metadata.tables[table_name]

    return {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def _index_names(table_name: str) -> set[str]:
    return {index.name for index in Base.metadata.tables[table_name].indexes}


def test_platform_admin_tables_are_registered() -> None:
    assert PlatformUser.__tablename__ in Base.metadata.tables
    assert PlatformRole.__tablename__ in Base.metadata.tables
    assert PlatformPermission.__tablename__ in Base.metadata.tables
    assert PlatformUserRole.__tablename__ in Base.metadata.tables
    assert PlatformRolePermission.__tablename__ in Base.metadata.tables


def test_platform_tables_do_not_include_tenant_id() -> None:
    for table_name in (
        "platform_users",
        "platform_roles",
        "platform_permissions",
        "platform_user_roles",
        "platform_role_permissions",
    ):
        assert "tenant_id" not in Base.metadata.tables[table_name].columns


def test_platform_user_table_columns_and_constraints() -> None:
    table = Base.metadata.tables["platform_users"]

    assert {
        "id",
        "email",
        "password_hash",
        "status",
        "is_super_admin",
        "email_verified_at",
        "last_login_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert ("email",) in _unique_constraint_columns("platform_users")
    assert "ix_platform_users_status" in _index_names("platform_users")
    assert "plain_password" not in table.columns
    assert "password" not in table.columns


def test_platform_role_slug_is_unique() -> None:
    assert ("slug",) in _unique_constraint_columns("platform_roles")


def test_platform_permission_key_is_unique() -> None:
    assert ("key",) in _unique_constraint_columns("platform_permissions")
    assert "ix_platform_permissions_category" in _index_names("platform_permissions")


def test_platform_user_roles_prevent_duplicate_assignments() -> None:
    table = Base.metadata.tables["platform_user_roles"]

    assert (
        "platform_user_id",
        "platform_role_id",
    ) in _unique_constraint_columns("platform_user_roles")
    assert "created_at" in table.columns
    assert "updated_at" not in table.columns
    assert (
        next(iter(table.c.platform_user_id.foreign_keys)).target_fullname
        == "platform_users.id"
    )
    assert (
        next(iter(table.c.platform_role_id.foreign_keys)).target_fullname
        == "platform_roles.id"
    )


def test_platform_role_permissions_prevent_duplicate_assignments() -> None:
    table = Base.metadata.tables["platform_role_permissions"]

    assert (
        "platform_role_id",
        "platform_permission_id",
    ) in _unique_constraint_columns("platform_role_permissions")
    assert "created_at" in table.columns
    assert "updated_at" not in table.columns
    assert (
        next(iter(table.c.platform_role_id.foreign_keys)).target_fullname
        == "platform_roles.id"
    )
    assert (
        next(iter(table.c.platform_permission_id.foreign_keys)).target_fullname
        == "platform_permissions.id"
    )
