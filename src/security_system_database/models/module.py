"""System module catalog model."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class Module(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Catalog entry for platform and tenant modules."""

    __tablename__ = "modules"
    __table_args__ = (
        CheckConstraint("key = lower(key)", name="key_lowercase"),
        CheckConstraint(
            "module_group IN ('platform', 'tenant')",
            name="module_group_valid",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'deprecated', 'coming_soon')",
            name="status_valid",
        ),
        UniqueConstraint("key", name="uq_modules_key"),
        Index("ix_modules_module_group", "module_group"),
        Index("ix_modules_status", "status"),
        Index("ix_modules_is_plan_assignable", "is_plan_assignable"),
        Index("ix_modules_is_add_on", "is_add_on"),
    )

    key: Mapped[str] = mapped_column(String(160), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    module_group: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    is_plan_assignable: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
    is_add_on: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
