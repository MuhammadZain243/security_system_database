"""Platform-managed configuration setting model."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    false,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

type JsonValue = dict[str, object] | list[object] | str | int | float | bool | None


class PlatformSetting(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """General platform-level setting managed outside infrastructure env vars."""

    __tablename__ = "platform_settings"
    __table_args__ = (
        CheckConstraint("key = lower(key)", name="key_lowercase"),
        CheckConstraint(
            "value_type IN ('string', 'boolean', 'number', 'json')",
            name="value_type_valid",
        ),
        UniqueConstraint("key", name="uq_platform_settings_key"),
        Index("ix_platform_settings_is_sensitive", "is_sensitive"),
        Index("ix_platform_settings_value_type", "value_type"),
    )

    key: Mapped[str] = mapped_column(String(160), nullable=False)
    value: Mapped[JsonValue] = mapped_column(JSONB, nullable=True)
    value_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
