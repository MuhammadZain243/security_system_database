"""General platform configuration model."""

from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    false,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from security_system_database.models.types import UUID_TYPE

type JsonValue = dict[str, object] | list[object] | str | int | float | bool | None


class PlatformConfiguration(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
):
    """Platform-owned operational configuration profile."""

    __tablename__ = "platform_configurations"
    __table_args__ = (
        CheckConstraint("key = lower(key)", name="key_lowercase"),
        CheckConstraint(
            "config_type IN ("
            "'email', "
            "'calendar', "
            "'payment', "
            "'notification', "
            "'security', "
            "'storage', "
            "'maps', "
            "'general'"
            ")",
            name="config_type_valid",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'needs_setup', 'error')",
            name="status_valid",
        ),
        Index("ix_platform_configurations_config_type", "config_type"),
        Index(
            "ix_platform_configurations_integration_connection_id",
            "integration_connection_id",
        ),
        Index("ix_platform_configurations_is_default", "is_default"),
        Index("ix_platform_configurations_is_sensitive", "is_sensitive"),
        Index("ix_platform_configurations_key", "key"),
        Index("ix_platform_configurations_status", "status"),
        Index(
            "uq_platform_configurations_type_key_active",
            "config_type",
            "key",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_platform_configurations_one_active_default_per_type",
            "config_type",
            unique=True,
            postgresql_where=text(
                "is_default = true AND status = 'active' AND deleted_at IS NULL"
            ),
        ),
    )

    config_type: Mapped[str] = mapped_column(String(40), nullable=False)
    key: Mapped[str] = mapped_column(String(160), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    integration_connection_id: Mapped[UUID | None] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "platform_integration_connections.id",
            name="fk_platform_configurations_integration_connection_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    value: Mapped[JsonValue] = mapped_column(
        JSONB,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    encrypted_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'needs_setup'"),
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
    metadata_: Mapped[JsonValue] = mapped_column(
        "metadata",
        JSONB,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
