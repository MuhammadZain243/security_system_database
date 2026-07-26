"""Tests for shared SQLAlchemy model mixins."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from security_system_database.models import (
    AuditActorMixin,
    SoftDeleteMixin,
    TenantOwnershipMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ModelTestBase(DeclarativeBase):
    """Isolated base for mixin tests."""

    metadata = MetaData()


class Tenant(ModelTestBase, UUIDPrimaryKeyMixin):
    """Minimal tenant table for foreign key resolution."""

    __tablename__ = "tenants"


class ExampleTenantModel(
    ModelTestBase,
    UUIDPrimaryKeyMixin,
    TenantOwnershipMixin,
    TimestampMixin,
    SoftDeleteMixin,
    AuditActorMixin,
):
    """Concrete model used only for inspecting mixin columns."""

    __tablename__ = "example_tenant_models"

    name: Mapped[str] = mapped_column(nullable=False)


def test_uuid_primary_key_mixin_adds_uuid_id_column() -> None:
    id_column = ExampleTenantModel.__table__.c.id

    assert id_column.primary_key is True
    assert id_column.default is not None
    assert id_column.type.as_uuid is True


def test_timestamp_mixin_adds_required_timestamp_columns() -> None:
    created_at = ExampleTenantModel.__table__.c.created_at
    updated_at = ExampleTenantModel.__table__.c.updated_at

    assert created_at.nullable is False
    assert updated_at.nullable is False
    assert created_at.server_default is not None
    assert updated_at.server_default is not None
    assert created_at.type.timezone is True
    assert updated_at.type.timezone is True


def test_soft_delete_mixin_adds_nullable_deleted_at_column() -> None:
    deleted_at = ExampleTenantModel.__table__.c.deleted_at

    assert deleted_at.nullable is True
    assert deleted_at.type.timezone is True


def test_tenant_ownership_mixin_adds_tenant_id_with_index() -> None:
    tenant_id = ExampleTenantModel.__table__.c.tenant_id
    tenant_indexes = {index.name for index in ExampleTenantModel.__table__.indexes}

    assert tenant_id.nullable is False
    assert tenant_id.type.as_uuid is True
    assert "ix_example_tenant_models_tenant_id" in tenant_indexes


def test_tenant_ownership_mixin_adds_tenant_foreign_key() -> None:
    foreign_keys = list(ExampleTenantModel.__table__.c.tenant_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert isinstance(foreign_keys[0], ForeignKey)
    assert foreign_keys[0].target_fullname == "tenants.id"


def test_audit_actor_mixin_adds_nullable_uuid_columns() -> None:
    for column_name in (
        "created_by_user_id",
        "updated_by_user_id",
        "deleted_by_user_id",
    ):
        column = ExampleTenantModel.__table__.c[column_name]

        assert column.nullable is True
        assert column.type.as_uuid is True


def test_mixin_annotations_expose_expected_python_types() -> None:
    assert UUIDPrimaryKeyMixin.__annotations__["id"] == Mapped[UUID]
    assert TimestampMixin.__annotations__["created_at"] == Mapped[datetime]
    assert SoftDeleteMixin.__annotations__["deleted_at"] == Mapped[datetime | None]
