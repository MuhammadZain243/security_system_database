"""Platform administrator permission model."""

from sqlalchemy import CheckConstraint, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PlatformPermission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stable permission definition for platform administrator access."""

    __tablename__ = "platform_permissions"
    __table_args__ = (
        CheckConstraint("key = lower(key)", name="platform_permissions_key_lowercase"),
        UniqueConstraint("key", name="uq_platform_permissions_key"),
        Index("ix_platform_permissions_category", "category"),
    )

    key: Mapped[str] = mapped_column(String(160), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
