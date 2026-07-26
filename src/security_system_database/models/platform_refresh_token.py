"""Platform refresh token model."""

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


class PlatformRefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Refresh token record for a platform user session."""

    __tablename__ = "platform_refresh_tokens"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'revoked', 'expired', 'rotated')",
            name="status_valid",
        ),
        UniqueConstraint("token_hash", name="uq_platform_refresh_tokens_token_hash"),
        Index("ix_platform_refresh_tokens_expires_at", "expires_at"),
        Index("ix_platform_refresh_tokens_platform_user_id", "platform_user_id"),
        Index("ix_platform_refresh_tokens_session_id", "session_id"),
        Index("ix_platform_refresh_tokens_status", "status"),
    )

    platform_user_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_users.id",
            name="fk_platform_refresh_tokens_platform_user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    session_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_user_sessions.id",
            name="fk_platform_refresh_tokens_session_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
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
    rotated_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
