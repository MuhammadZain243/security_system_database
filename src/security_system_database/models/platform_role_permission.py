"""Platform administrator role-permission assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class PlatformRolePermission(Base, UUIDPrimaryKeyMixin):
    """Assignment of a platform permission to a platform role."""

    __tablename__ = "platform_role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "platform_role_id",
            "platform_permission_id",
            name="uq_platform_role_permissions_role_permission",
        ),
        Index(
            "ix_platform_role_permissions_platform_permission_id",
            "platform_permission_id",
        ),
        Index("ix_platform_role_permissions_platform_role_id", "platform_role_id"),
    )

    platform_role_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("platform_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    platform_permission_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("platform_permissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
