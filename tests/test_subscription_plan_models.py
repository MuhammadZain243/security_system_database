"""Tests for subscription plan and add-on models."""

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint

from security_system_database import Base
from security_system_database.models import (
    AddOn,
    AddOnModule,
    SubscriptionPlan,
    SubscriptionPlanLimit,
    SubscriptionPlanModule,
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


def test_subscription_plan_tables_are_registered() -> None:
    assert SubscriptionPlan.__tablename__ in Base.metadata.tables
    assert SubscriptionPlanModule.__tablename__ in Base.metadata.tables
    assert SubscriptionPlanLimit.__tablename__ in Base.metadata.tables
    assert AddOn.__tablename__ in Base.metadata.tables
    assert AddOnModule.__tablename__ in Base.metadata.tables


def test_subscription_plan_and_add_on_tables_do_not_include_tenant_id() -> None:
    for table_name in (
        "subscription_plans",
        "subscription_plan_modules",
        "subscription_plan_limits",
        "add_ons",
        "add_on_modules",
    ):
        assert "tenant_id" not in Base.metadata.tables[table_name].columns


def test_subscription_plan_columns_constraints_and_indexes() -> None:
    table = Base.metadata.tables["subscription_plans"]

    assert {
        "id",
        "name",
        "slug",
        "description",
        "status",
        "billing_interval",
        "price_amount",
        "currency",
        "trial_days",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert ("slug",) in _unique_constraint_columns("subscription_plans")
    assert "ck_subscription_plans_slug_lowercase" in _check_constraint_names(
        "subscription_plans"
    )
    assert "ck_subscription_plans_currency_uppercase" in _check_constraint_names(
        "subscription_plans"
    )
    assert "ck_subscription_plans_currency_length_valid" in _check_constraint_names(
        "subscription_plans"
    )
    assert "ck_subscription_plans_status_valid" in _check_constraint_names(
        "subscription_plans"
    )
    assert "ck_subscription_plans_billing_interval_valid" in _check_constraint_names(
        "subscription_plans"
    )
    assert "ck_subscription_plans_price_amount_non_negative" in (
        _check_constraint_names("subscription_plans")
    )
    assert "ck_subscription_plans_trial_days_non_negative" in _check_constraint_names(
        "subscription_plans"
    )
    assert "ix_subscription_plans_billing_interval" in _index_names(
        "subscription_plans"
    )
    assert "ix_subscription_plans_status" in _index_names("subscription_plans")
    assert table.c.status.server_default is not None
    assert table.c.trial_days.server_default is not None


def test_subscription_plan_module_constraints_and_foreign_keys() -> None:
    table = Base.metadata.tables["subscription_plan_modules"]

    assert {
        "id",
        "subscription_plan_id",
        "module_id",
        "created_at",
    }.issubset(table.columns.keys())
    assert ("subscription_plan_id", "module_id") in _unique_constraint_columns(
        "subscription_plan_modules"
    )
    assert "ix_subscription_plan_modules_subscription_plan_id" in _index_names(
        "subscription_plan_modules"
    )
    assert "ix_subscription_plan_modules_module_id" in _index_names(
        "subscription_plan_modules"
    )

    subscription_plan_fks = list(table.c.subscription_plan_id.foreign_keys)
    module_fks = list(table.c.module_id.foreign_keys)

    assert len(subscription_plan_fks) == 1
    assert isinstance(subscription_plan_fks[0], ForeignKey)
    assert subscription_plan_fks[0].name == "fk_subscription_plan_modules_plan_id"
    assert subscription_plan_fks[0].target_fullname == "subscription_plans.id"
    assert subscription_plan_fks[0].ondelete == "CASCADE"
    assert len(module_fks) == 1
    assert isinstance(module_fks[0], ForeignKey)
    assert module_fks[0].name == "fk_subscription_plan_modules_module_id"
    assert module_fks[0].target_fullname == "modules.id"
    assert module_fks[0].ondelete == "RESTRICT"


def test_subscription_plan_limit_constraints_and_foreign_key() -> None:
    table = Base.metadata.tables["subscription_plan_limits"]

    assert {
        "id",
        "subscription_plan_id",
        "limit_key",
        "limit_value",
        "created_at",
        "updated_at",
    }.issubset(table.columns.keys())
    assert ("subscription_plan_id", "limit_key") in _unique_constraint_columns(
        "subscription_plan_limits"
    )
    assert "ck_subscription_plan_limits_limit_key_valid" in _check_constraint_names(
        "subscription_plan_limits"
    )
    assert "ck_subscription_plan_limits_limit_value_non_negative" in (
        _check_constraint_names("subscription_plan_limits")
    )
    assert "ix_subscription_plan_limits_limit_key" in _index_names(
        "subscription_plan_limits"
    )
    assert "ix_subscription_plan_limits_subscription_plan_id" in _index_names(
        "subscription_plan_limits"
    )

    foreign_keys = list(table.c.subscription_plan_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)
    assert foreign_keys[0].name == "fk_subscription_plan_limits_plan_id"
    assert foreign_keys[0].target_fullname == "subscription_plans.id"
    assert foreign_keys[0].ondelete == "CASCADE"


def test_add_on_columns_constraints_and_indexes() -> None:
    table = Base.metadata.tables["add_ons"]

    assert {
        "id",
        "name",
        "slug",
        "description",
        "status",
        "billing_interval",
        "price_amount",
        "currency",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(table.columns.keys())
    assert ("slug",) in _unique_constraint_columns("add_ons")
    assert "ck_add_ons_slug_lowercase" in _check_constraint_names("add_ons")
    assert "ck_add_ons_currency_uppercase" in _check_constraint_names("add_ons")
    assert "ck_add_ons_currency_length_valid" in _check_constraint_names("add_ons")
    assert "ck_add_ons_status_valid" in _check_constraint_names("add_ons")
    assert "ck_add_ons_billing_interval_valid" in _check_constraint_names("add_ons")
    assert "ck_add_ons_price_amount_non_negative" in _check_constraint_names("add_ons")
    assert "ix_add_ons_billing_interval" in _index_names("add_ons")
    assert "ix_add_ons_status" in _index_names("add_ons")
    assert table.c.status.server_default is not None


def test_add_on_module_constraints_and_foreign_keys() -> None:
    table = Base.metadata.tables["add_on_modules"]

    assert {
        "id",
        "add_on_id",
        "module_id",
        "created_at",
    }.issubset(table.columns.keys())
    assert ("add_on_id", "module_id") in _unique_constraint_columns("add_on_modules")
    assert "ix_add_on_modules_add_on_id" in _index_names("add_on_modules")
    assert "ix_add_on_modules_module_id" in _index_names("add_on_modules")

    add_on_fks = list(table.c.add_on_id.foreign_keys)
    module_fks = list(table.c.module_id.foreign_keys)

    assert len(add_on_fks) == 1
    assert isinstance(add_on_fks[0], ForeignKey)
    assert add_on_fks[0].name == "fk_add_on_modules_add_on_id"
    assert add_on_fks[0].target_fullname == "add_ons.id"
    assert add_on_fks[0].ondelete == "CASCADE"
    assert len(module_fks) == 1
    assert isinstance(module_fks[0], ForeignKey)
    assert module_fks[0].name == "fk_add_on_modules_module_id"
    assert module_fks[0].target_fullname == "modules.id"
    assert module_fks[0].ondelete == "RESTRICT"
