"""Platform integration provider model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from security_system_database.models.platform_oauth_config import (
        PlatformOAuthConfig,
    )


class PlatformIntegrationProvider(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
):
    """Integration provider supported by the platform owner configuration area."""

    __tablename__ = "platform_integration_providers"
    __table_args__ = (
        CheckConstraint(
            "provider_key = lower(provider_key)", name="provider_key_lowercase"
        ),
        CheckConstraint(
            "category IN ('oauth', 'payment', 'email', 'sms', 'storage', 'calendar', 'maps')",
            name="category_valid",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name="status_valid",
        ),
        UniqueConstraint("provider_key", name="uq_platform_integration_providers_key"),
        Index("ix_platform_integration_providers_category", "category"),
        Index("ix_platform_integration_providers_status", "status"),
    )

    provider_key: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'active'"),
        nullable=False,
    )

    oauth_config: Mapped[PlatformOAuthConfig | None] = relationship(
        "PlatformOAuthConfig",
        back_populates="provider",
        uselist=False,
    )
