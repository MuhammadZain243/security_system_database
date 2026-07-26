"""Platform administrator role model."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


class PlatformRole(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Internal platform role used for platform administrator access."""

    __tablename__ = "platform_roles"
    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="platform_roles_slug_lowercase"),
        UniqueConstraint("slug", name="uq_platform_roles_slug"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
