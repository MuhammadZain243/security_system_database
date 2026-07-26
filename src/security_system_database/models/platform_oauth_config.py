"""Platform OAuth provider configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from security_system_database.models.types import UUID_TYPE

if TYPE_CHECKING:
    from security_system_database.models.platform_integration_provider import (
        PlatformIntegrationProvider,
    )


class PlatformOAuthConfig(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """OAuth settings for a platform-supported integration provider."""

    __tablename__ = "platform_oauth_configs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'needs_setup')",
            name="status_valid",
        ),
        UniqueConstraint("provider_id", name="uq_platform_oauth_configs_provider_id"),
        Index("ix_platform_oauth_configs_status", "status"),
    )

    provider_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_integration_providers.id",
            name="fk_platform_oauth_configs_provider_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    client_secret_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    redirect_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default=text("'[]'::jsonb"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'needs_setup'"),
        nullable=False,
    )

    provider: Mapped[PlatformIntegrationProvider] = relationship(
        "PlatformIntegrationProvider",
        back_populates="oauth_config",
    )
