"""Platform authentication event model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE

type JsonValue = dict[str, object] | list[object] | str | int | float | bool | None


class PlatformAuthEvent(Base, UUIDPrimaryKeyMixin):
    """Append-only authentication audit event for platform users."""

    __tablename__ = "platform_auth_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'login_success', "
            "'login_failed', "
            "'logout', "
            "'session_revoked', "
            "'refresh_token_rotated', "
            "'password_reset_requested', "
            "'password_reset_completed', "
            "'email_verification_requested', "
            "'email_verified'"
            ")",
            name="event_type_valid",
        ),
        Index("ix_platform_auth_events_created_at", "created_at"),
        Index("ix_platform_auth_events_event_type", "event_type"),
        Index("ix_platform_auth_events_platform_user_id", "platform_user_id"),
    )

    platform_user_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_users.id",
            name="fk_platform_auth_events_platform_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    metadata_: Mapped[JsonValue] = mapped_column(
        "metadata",
        JSONB,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
