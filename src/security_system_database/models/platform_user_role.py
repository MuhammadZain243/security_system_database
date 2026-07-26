"""Platform administrator user-role assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class PlatformUserRole(Base, UUIDPrimaryKeyMixin):
    """Assignment of a platform role to a platform user."""

    __tablename__ = "platform_user_roles"
    __table_args__ = (
        UniqueConstraint(
            "platform_user_id",
            "platform_role_id",
            name="uq_platform_user_roles_user_role",
        ),
        Index("ix_platform_user_roles_platform_role_id", "platform_role_id"),
        Index("ix_platform_user_roles_platform_user_id", "platform_user_id"),
    )

    platform_user_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("platform_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    platform_role_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("platform_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
