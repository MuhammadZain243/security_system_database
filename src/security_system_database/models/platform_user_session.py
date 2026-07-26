"""Platform user login session model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class PlatformUserSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Login session for an internal platform user."""

    __tablename__ = "platform_user_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'revoked', 'expired')",
            name="status_valid",
        ),
        UniqueConstraint(
            "session_token_hash",
            name="uq_platform_user_sessions_session_token_hash",
        ),
        UniqueConstraint(
            "platform_user_id",
            "id",
            name="uq_platform_user_sessions_platform_user_id_id",
        ),
        Index("ix_platform_user_sessions_expires_at", "expires_at"),
        Index("ix_platform_user_sessions_platform_user_id", "platform_user_id"),
        Index("ix_platform_user_sessions_status", "status"),
    )

    platform_user_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_users.id",
            name="fk_platform_user_sessions_platform_user_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    session_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'active'"),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DATETIME_TIMEZONE, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
