"""Platform user invitation model."""

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


class PlatformUserInvitation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Invitation for an internal platform user."""

    __tablename__ = "platform_user_invitations"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'expired', 'revoked')",
            name="status_valid",
        ),
        UniqueConstraint(
            "token_hash",
            name="uq_platform_user_invitations_token_hash",
        ),
        Index(
            "ix_platform_user_invitations_accepted_platform_user_id",
            "accepted_platform_user_id",
        ),
        Index("ix_platform_user_invitations_email", "email"),
        Index("ix_platform_user_invitations_expires_at", "expires_at"),
        Index(
            "ix_platform_user_invitations_invited_by_platform_user_id",
            "invited_by_platform_user_id",
        ),
        Index("ix_platform_user_invitations_status", "status"),
        Index(
            "uq_platform_user_invitations_one_pending_per_email",
            "email",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'pending'"),
        nullable=False,
    )
    invited_by_platform_user_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_users.id",
            name="fk_platform_user_invitations_invited_by_platform_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    accepted_platform_user_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_users.id",
            name="fk_platform_user_invitations_accepted_platform_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DATETIME_TIMEZONE, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
