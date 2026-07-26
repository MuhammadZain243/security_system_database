"""Platform administrator user model."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Index, String, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from security_system_database.models.types import DATETIME_TIMEZONE


class PlatformUser(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Internal platform user for SaaS owner/admin operations."""

    __tablename__ = "platform_users"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'locked')",
            name="platform_users_status_valid",
        ),
        UniqueConstraint("email", name="uq_platform_users_email"),
        Index("ix_platform_users_email", "email"),
        Index("ix_platform_users_status", "status"),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    is_super_admin: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
