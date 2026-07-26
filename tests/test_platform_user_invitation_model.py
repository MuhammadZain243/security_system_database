"""Tests for platform user invitation models."""

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint

from security_system_database import Base
from security_system_database.models import (
    PlatformUserInvitation,
    PlatformUserInvitationRole,
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
    raw_token_columns = {"token", "invitation_token"}

    assert raw_token_columns.isdisjoint(Base.metadata.tables[table_name].columns.keys())


def test_platform_user_invitation_tables_are_registered() -> None:
    assert PlatformUserInvitation.__tablename__ in Base.metadata.tables
    assert PlatformUserInvitationRole.__tablename__ in Base.metadata.tables


def test_platform_user_invitation_columns_constraints_indexes_and_tokens() -> None:
    table = Base.metadata.tables["platform_user_invitations"]

    assert {
        "id",
        "email",
        "token_hash",
        "status",
        "invited_by_platform_user_id",
        "accepted_platform_user_id",
        "expires_at",
        "accepted_at",
        "revoked_at",
        "created_at",
        "updated_at",
    }.issubset(table.columns.keys())
    assert not table.c.email.nullable
    assert ("token_hash",) in _unique_constraint_columns("platform_user_invitations")
    assert "ck_platform_user_invitations_email_lowercase" in _check_constraint_names(
        "platform_user_invitations"
    )
    assert "ck_platform_user_invitations_status_valid" in _check_constraint_names(
        "platform_user_invitations"
    )
    assert "ix_platform_user_invitations_email" in _index_names(
        "platform_user_invitations"
    )
    assert "ix_platform_user_invitations_status" in _index_names(
        "platform_user_invitations"
    )
    assert "ix_platform_user_invitations_expires_at" in _index_names(
        "platform_user_invitations"
    )
    assert "ix_platform_user_invitations_invited_by_platform_user_id" in _index_names(
        "platform_user_invitations"
    )
    assert "ix_platform_user_invitations_accepted_platform_user_id" in _index_names(
        "platform_user_invitations"
    )
    pending_email_index = _index_by_name(
        "platform_user_invitations",
        "uq_platform_user_invitations_one_pending_per_email",
    )

    assert pending_email_index.unique
    assert tuple(pending_email_index.columns.keys()) == ("email",)
    assert str(pending_email_index.dialect_options["postgresql"]["where"]) == (
        "status = 'pending'"
    )
    assert table.c.status.server_default is not None
    _assert_no_raw_token_columns("platform_user_invitations")


def test_platform_user_invitation_user_foreign_keys() -> None:
    invited_by_fk = _foreign_key_by_column(
        "platform_user_invitations",
        "invited_by_platform_user_id",
    )
    accepted_user_fk = _foreign_key_by_column(
        "platform_user_invitations",
        "accepted_platform_user_id",
    )

    assert (
        invited_by_fk.name == "fk_platform_user_invitations_invited_by_platform_user_id"
    )
    assert invited_by_fk.target_fullname == "platform_users.id"
    assert invited_by_fk.ondelete == "SET NULL"
    assert (
        accepted_user_fk.name
        == "fk_platform_user_invitations_accepted_platform_user_id"
    )
    assert accepted_user_fk.target_fullname == "platform_users.id"
    assert accepted_user_fk.ondelete == "SET NULL"


def test_platform_user_invitation_role_columns_constraints_indexes_and_foreign_keys() -> (
    None
):
    table = Base.metadata.tables["platform_user_invitation_roles"]

    assert {
        "id",
        "platform_user_invitation_id",
        "platform_role_id",
        "created_at",
    }.issubset(table.columns.keys())
    assert (
        "platform_user_invitation_id",
        "platform_role_id",
    ) in _unique_constraint_columns("platform_user_invitation_roles")
    assert "ix_platform_user_invitation_roles_invitation_id" in _index_names(
        "platform_user_invitation_roles"
    )
    assert "ix_platform_user_invitation_roles_role_id" in _index_names(
        "platform_user_invitation_roles"
    )
    assert table.c.created_at.server_default is not None

    invitation_fk = _foreign_key_by_column(
        "platform_user_invitation_roles",
        "platform_user_invitation_id",
    )
    role_fk = _foreign_key_by_column(
        "platform_user_invitation_roles",
        "platform_role_id",
    )

    assert invitation_fk.name == "fk_platform_user_invitation_roles_invitation_id"
    assert invitation_fk.target_fullname == "platform_user_invitations.id"
    assert invitation_fk.ondelete == "CASCADE"
    assert role_fk.name == "fk_platform_user_invitation_roles_role_id"
    assert role_fk.target_fullname == "platform_roles.id"
    assert role_fk.ondelete == "RESTRICT"
