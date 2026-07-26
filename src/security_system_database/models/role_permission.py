"""Tenant role-permission assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class RolePermission(Base, UUIDPrimaryKeyMixin):
    """Assignment of a tenant permission to a tenant role."""

    __tablename__ = "role_permissions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "role_id"],
            ["roles.tenant_id", "roles.id"],
            name="fk_role_permissions_tenant_role",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "tenant_id",
            "role_id",
            "permission_id",
            name="uq_role_permissions_tenant_role_permission",
        ),
        Index("ix_role_permissions_permission_id", "permission_id"),
        Index("ix_role_permissions_role_id", "role_id"),
        Index("ix_role_permissions_tenant_id", "tenant_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "tenants.id",
            name="fk_role_permissions_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    role_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        nullable=False,
    )
    permission_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "permissions.id",
            name="fk_role_permissions_permission_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
