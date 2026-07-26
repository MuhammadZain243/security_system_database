"""Platform integration connection model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE

type JsonValue = dict[str, object] | list[object] | str | int | float | bool | None


class PlatformIntegrationConnection(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
):
    """Connected third-party account for platform-managed integrations."""

    __tablename__ = "platform_integration_connections"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'needs_reconnect', 'revoked', 'error')",
            name="status_valid",
        ),
        Index(
            "ix_platform_integration_connections_connected_by_user_id",
            "connected_by_platform_user_id",
        ),
        Index(
            "ix_platform_integration_connections_external_account_email",
            "external_account_email",
        ),
        Index("ix_platform_integration_connections_provider_id", "provider_id"),
        Index("ix_platform_integration_connections_status", "status"),
        Index(
            "ix_platform_integration_connections_token_expires_at",
            "token_expires_at",
        ),
        Index(
            "uq_platform_integration_connections_provider_external_account",
            "provider_id",
            "external_account_id",
            unique=True,
            postgresql_where=text("external_account_id IS NOT NULL"),
        ),
    )

    provider_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_integration_providers.id",
            name="fk_platform_integration_connections_provider_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    connected_by_platform_user_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_users.id",
            name="fk_platform_integration_connections_connected_by_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    external_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_account_email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    scopes: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default=text("'[]'::jsonb"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'active'"),
        nullable=False,
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[JsonValue] = mapped_column(
        "metadata",
        JSONB,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
