"""Tests for tenant user and RBAC foundation models."""

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
)

from security_system_database import Base
from security_system_database.models import (
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
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


def _foreign_key_constraint_names(table_name: str) -> set[str]:
    return {
        constraint.name or ""
        for constraint in Base.metadata.tables[table_name].foreign_key_constraints
    }


def _foreign_key_constraint_by_name(
    table_name: str,
    constraint_name: str,
) -> ForeignKeyConstraint:
    matching_constraints = [
        constraint
        for constraint in Base.metadata.tables[table_name].foreign_key_constraints
        if constraint.name == constraint_name
    ]

    assert len(matching_constraints) == 1

    return matching_constraints[0]


def _foreign_key_constraint_targets(
    constraint: ForeignKeyConstraint,
) -> tuple[tuple[str, ...], tuple[str, ...], set[str | None]]:
    return (
        tuple(constraint.columns.keys()),
        tuple(element.target_fullname for element in constraint.elements),
        {element.ondelete for element in constraint.elements},
    )


def test_tenant_user_rbac_tables_are_registered() -> None:
    assert User.__tablename__ in Base.metadata.tables
    assert Role.__tablename__ in Base.metadata.tables
    assert Permission.__tablename__ in Base.metadata.tables
    assert UserRole.__tablename__ in Base.metadata.tables
    assert RolePermission.__tablename__ in Base.metadata.tables


def test_tenant_owned_rbac_tables_include_tenant_id() -> None:
    for table_name in ("users", "roles", "user_roles", "role_permissions"):
        assert "tenant_id" in Base.metadata.tables[table_name].columns


def test_permission_table_is_global_and_has_no_tenant_id() -> None:
    assert "tenant_id" not in Base.metadata.tables["permissions"].columns


def test_user_columns_constraints_indexes_and_password_storage() -> None:
    table = Base.metadata.tables["users"]

    assert {
        "id",
        "tenant_id",
        "email",
        "password_hash",
        "first_name",
        "last_name",
        "phone",
        "status",
        "email_verified_at",
        "last_login_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert "password" not in table.columns
    assert ("tenant_id", "email") in _unique_constraint_columns("users")
    assert ("tenant_id", "id") in _unique_constraint_columns("users")
    assert "ck_users_email_lowercase" in _check_constraint_names("users")
    assert "ck_users_status_valid" in _check_constraint_names("users")
    assert "ix_users_tenant_id" in _index_names("users")
    assert "ix_users_email" in _index_names("users")
    assert "ix_users_status" in _index_names("users")
    assert table.c.status.server_default is not None

    tenant_fk = _foreign_key_by_column("users", "tenant_id")

    assert tenant_fk.name == "fk_users_tenant_id"
    assert tenant_fk.target_fullname == "tenants.id"
    assert tenant_fk.ondelete == "RESTRICT"


def test_role_columns_constraints_indexes_and_tenant_fk() -> None:
    table = Base.metadata.tables["roles"]

    assert {
        "id",
        "tenant_id",
        "name",
        "slug",
        "description",
        "is_system",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert ("tenant_id", "slug") in _unique_constraint_columns("roles")
    assert ("tenant_id", "id") in _unique_constraint_columns("roles")
    assert "ck_roles_slug_lowercase" in _check_constraint_names("roles")
    assert "ix_roles_tenant_id" in _index_names("roles")
    assert table.c.is_system.server_default is not None

    tenant_fk = _foreign_key_by_column("roles", "tenant_id")

    assert tenant_fk.name == "fk_roles_tenant_id"
    assert tenant_fk.target_fullname == "tenants.id"
    assert tenant_fk.ondelete == "RESTRICT"


def test_permission_columns_constraints_and_indexes() -> None:
    table = Base.metadata.tables["permissions"]

    assert {
        "id",
        "key",
        "name",
        "description",
        "category",
        "created_at",
        "updated_at",
    }.issubset(table.columns.keys())
    assert ("key",) in _unique_constraint_columns("permissions")
    assert "ck_permissions_key_lowercase" in _check_constraint_names("permissions")
    assert "ix_permissions_category" in _index_names("permissions")


def test_user_role_assignment_constraints_and_foreign_keys() -> None:
    table = Base.metadata.tables["user_roles"]

    assert {"id", "tenant_id", "user_id", "role_id", "created_at"}.issubset(
        table.columns.keys()
    )
    assert ("tenant_id", "user_id", "role_id") in _unique_constraint_columns(
        "user_roles"
    )
    assert "ix_user_roles_tenant_id" in _index_names("user_roles")
    assert "ix_user_roles_user_id" in _index_names("user_roles")
    assert "ix_user_roles_role_id" in _index_names("user_roles")

    foreign_key_constraints = _foreign_key_constraint_names("user_roles")

    assert "fk_user_roles_tenant_id" in foreign_key_constraints
    assert "fk_user_roles_tenant_user" in foreign_key_constraints
    assert "fk_user_roles_tenant_role" in foreign_key_constraints
    assert _foreign_key_constraint_targets(
        _foreign_key_constraint_by_name("user_roles", "fk_user_roles_tenant_user")
    ) == (
        ("tenant_id", "user_id"),
        ("users.tenant_id", "users.id"),
        {"CASCADE"},
    )
    assert _foreign_key_constraint_targets(
        _foreign_key_constraint_by_name("user_roles", "fk_user_roles_tenant_role")
    ) == (
        ("tenant_id", "role_id"),
        ("roles.tenant_id", "roles.id"),
        {"CASCADE"},
    )


def test_role_permission_assignment_constraints_and_foreign_keys() -> None:
    table = Base.metadata.tables["role_permissions"]

    assert {"id", "tenant_id", "role_id", "permission_id", "created_at"}.issubset(
        table.columns.keys()
    )
    assert ("tenant_id", "role_id", "permission_id") in _unique_constraint_columns(
        "role_permissions"
    )
    assert "ix_role_permissions_tenant_id" in _index_names("role_permissions")
    assert "ix_role_permissions_role_id" in _index_names("role_permissions")
    assert "ix_role_permissions_permission_id" in _index_names("role_permissions")

    permission_fk = _foreign_key_by_column("role_permissions", "permission_id")
    foreign_key_constraints = _foreign_key_constraint_names("role_permissions")

    assert "fk_role_permissions_tenant_id" in foreign_key_constraints
    assert "fk_role_permissions_tenant_role" in foreign_key_constraints
    assert _foreign_key_constraint_targets(
        _foreign_key_constraint_by_name(
            "role_permissions",
            "fk_role_permissions_tenant_role",
        )
    ) == (
        ("tenant_id", "role_id"),
        ("roles.tenant_id", "roles.id"),
        {"CASCADE"},
    )
    assert permission_fk.name == "fk_role_permissions_permission_id"
    assert permission_fk.target_fullname == "permissions.id"
    assert permission_fk.ondelete == "CASCADE"
