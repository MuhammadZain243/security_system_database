"""Tests for the system module catalog model."""

from sqlalchemy import CheckConstraint, UniqueConstraint

from security_system_database import Base
from security_system_database.models import Module


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


def test_module_table_is_registered() -> None:
    assert Module.__tablename__ in Base.metadata.tables


def test_module_table_has_expected_columns() -> None:
    table = Base.metadata.tables["modules"]

    assert {
        "id",
        "key",
        "name",
        "description",
        "module_group",
        "status",
        "is_plan_assignable",
        "is_add_on",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())


def test_module_table_does_not_include_tenant_id() -> None:
    assert "tenant_id" not in Base.metadata.tables["modules"].columns


def test_module_constraints_and_indexes() -> None:
    assert ("key",) in _unique_constraint_columns("modules")
    assert "ck_modules_key_lowercase" in _check_constraint_names("modules")
    assert "ck_modules_module_group_valid" in _check_constraint_names("modules")
    assert "ck_modules_status_valid" in _check_constraint_names("modules")
    assert "ix_modules_module_group" in _index_names("modules")
    assert "ix_modules_status" in _index_names("modules")
    assert "ix_modules_is_plan_assignable" in _index_names("modules")
    assert "ix_modules_is_add_on" in _index_names("modules")
