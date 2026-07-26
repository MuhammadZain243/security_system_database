"""Tenant user-role assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class UserRole(Base, UUIDPrimaryKeyMixin):
    """Assignment of a tenant role to a tenant user."""

    __tablename__ = "user_roles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            name="fk_user_roles_tenant_user",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "role_id"],
            ["roles.tenant_id", "roles.id"],
            name="fk_user_roles_tenant_role",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "tenant_id", "user_id", "role_id", name="uq_user_roles_tenant_user_role"
        ),
        Index("ix_user_roles_role_id", "role_id"),
        Index("ix_user_roles_tenant_id", "tenant_id"),
        Index("ix_user_roles_user_id", "user_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "tenants.id",
            name="fk_user_roles_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        nullable=False,
    )
    role_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
