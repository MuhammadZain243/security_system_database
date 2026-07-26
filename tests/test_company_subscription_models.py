"""Tests for company subscription and add-on assignment models."""

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects import postgresql

from security_system_database import Base
from security_system_database.models import CompanyAddOn, CompanySubscription


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
    table = Base.metadata.tables[table_name]

    return next(index for index in table.indexes if index.name == index_name)


def _postgresql_where_text(index) -> str:
    where_clause = index.dialect_options["postgresql"]["where"]

    assert where_clause is not None
    return str(
        where_clause.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_company_subscription_assignment_tables_are_registered() -> None:
    assert CompanySubscription.__tablename__ in Base.metadata.tables
    assert CompanyAddOn.__tablename__ in Base.metadata.tables


def test_company_subscription_assignment_tables_do_not_include_tenant_id() -> None:
    assert "tenant_id" not in Base.metadata.tables["company_subscriptions"].columns
    assert "tenant_id" not in Base.metadata.tables["company_add_ons"].columns


def test_company_subscription_columns_constraints_indexes_and_partial_unique() -> None:
    table = Base.metadata.tables["company_subscriptions"]

    assert {
        "id",
        "company_id",
        "subscription_plan_id",
        "status",
        "started_at",
        "trial_ends_at",
        "current_period_starts_at",
        "current_period_ends_at",
        "cancelled_at",
        "ended_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert "ck_company_subscriptions_status_valid" in _check_constraint_names(
        "company_subscriptions"
    )
    assert "ix_company_subscriptions_company_id" in _index_names(
        "company_subscriptions"
    )
    assert "ix_company_subscriptions_subscription_plan_id" in _index_names(
        "company_subscriptions"
    )
    assert "ix_company_subscriptions_status" in _index_names("company_subscriptions")

    partial_unique_index = _index_by_name(
        "company_subscriptions",
        "uq_company_subscriptions_one_active_per_company",
    )

    assert partial_unique_index.unique is True
    assert tuple(partial_unique_index.columns.keys()) == ("company_id",)
    where_text = _postgresql_where_text(partial_unique_index)

    assert "trialing" in where_text
    assert "active" in where_text
    assert table.c.status.server_default is not None


def test_company_subscription_references_company_and_subscription_plan() -> None:
    table = Base.metadata.tables["company_subscriptions"]
    company_fks = list(table.c.company_id.foreign_keys)
    plan_fks = list(table.c.subscription_plan_id.foreign_keys)

    assert len(company_fks) == 1
    assert isinstance(company_fks[0], ForeignKey)
    assert company_fks[0].name == "fk_company_subscriptions_company_id"
    assert company_fks[0].target_fullname == "companies.id"
    assert company_fks[0].ondelete == "RESTRICT"
    assert len(plan_fks) == 1
    assert isinstance(plan_fks[0], ForeignKey)
    assert plan_fks[0].name == "fk_company_subscriptions_plan_id"
    assert plan_fks[0].target_fullname == "subscription_plans.id"
    assert plan_fks[0].ondelete == "RESTRICT"


def test_company_add_on_columns_constraints_indexes_and_partial_unique() -> None:
    table = Base.metadata.tables["company_add_ons"]

    assert {
        "id",
        "company_id",
        "add_on_id",
        "status",
        "started_at",
        "current_period_starts_at",
        "current_period_ends_at",
        "cancelled_at",
        "ended_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert "ck_company_add_ons_status_valid" in _check_constraint_names(
        "company_add_ons"
    )
    assert "ix_company_add_ons_company_id" in _index_names("company_add_ons")
    assert "ix_company_add_ons_add_on_id" in _index_names("company_add_ons")
    assert "ix_company_add_ons_status" in _index_names("company_add_ons")

    partial_unique_index = _index_by_name(
        "company_add_ons",
        "uq_company_add_ons_one_active_per_company_add_on",
    )

    assert partial_unique_index.unique is True
    assert tuple(partial_unique_index.columns.keys()) == ("company_id", "add_on_id")
    where_text = _postgresql_where_text(partial_unique_index)

    assert "status = 'active'" in where_text
    assert table.c.status.server_default is not None


def test_company_add_on_references_company_and_add_on() -> None:
    table = Base.metadata.tables["company_add_ons"]
    company_fks = list(table.c.company_id.foreign_keys)
    add_on_fks = list(table.c.add_on_id.foreign_keys)

    assert len(company_fks) == 1
    assert isinstance(company_fks[0], ForeignKey)
    assert company_fks[0].name == "fk_company_add_ons_company_id"
    assert company_fks[0].target_fullname == "companies.id"
    assert company_fks[0].ondelete == "RESTRICT"
    assert len(add_on_fks) == 1
    assert isinstance(add_on_fks[0], ForeignKey)
    assert add_on_fks[0].name == "fk_company_add_ons_add_on_id"
    assert add_on_fks[0].target_fullname == "add_ons.id"
    assert add_on_fks[0].ondelete == "RESTRICT"
