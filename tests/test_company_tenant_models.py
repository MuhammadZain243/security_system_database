"""Tests for company and tenant foundation models."""

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint

from security_system_database import Base
from security_system_database.models import Company, Tenant


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


def test_company_and_tenant_tables_are_registered() -> None:
    assert Company.__tablename__ in Base.metadata.tables
    assert Tenant.__tablename__ in Base.metadata.tables


def test_company_table_has_expected_columns() -> None:
    table = Base.metadata.tables["companies"]

    assert {
        "id",
        "name",
        "slug",
        "legal_name",
        "email",
        "phone",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())


def test_tenant_table_has_expected_columns() -> None:
    table = Base.metadata.tables["tenants"]

    assert {
        "id",
        "company_id",
        "name",
        "slug",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())


def test_company_and_tenant_tables_do_not_include_tenant_id() -> None:
    assert "tenant_id" not in Base.metadata.tables["companies"].columns
    assert "tenant_id" not in Base.metadata.tables["tenants"].columns


def test_company_constraints_and_indexes() -> None:
    assert ("slug",) in _unique_constraint_columns("companies")
    assert "ix_companies_email" in _index_names("companies")
    assert "ix_companies_status" in _index_names("companies")
    assert "ck_companies_slug_lowercase" in _check_constraint_names("companies")
    assert "ck_companies_status_valid" in _check_constraint_names("companies")


def test_tenant_constraints_and_indexes() -> None:
    assert ("slug",) in _unique_constraint_columns("tenants")
    assert ("company_id",) in _unique_constraint_columns("tenants")
    assert "ix_tenants_status" in _index_names("tenants")
    assert "ck_tenants_slug_lowercase" in _check_constraint_names("tenants")
    assert "ck_tenants_status_valid" in _check_constraint_names("tenants")


def test_tenant_references_company() -> None:
    foreign_keys = list(Base.metadata.tables["tenants"].c.company_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)
    assert foreign_keys[0].target_fullname == "companies.id"
    assert foreign_keys[0].ondelete == "RESTRICT"
