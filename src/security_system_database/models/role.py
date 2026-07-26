"""Tenant role model."""

from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
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
from security_system_database.models.types import UUID_TYPE


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Tenant-side role used to grant workspace permissions."""

    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="slug_lowercase"),
        UniqueConstraint("tenant_id", "id", name="uq_roles_tenant_id_id"),
        UniqueConstraint("tenant_id", "slug", name="uq_roles_tenant_slug"),
        Index("ix_roles_tenant_id", "tenant_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "tenants.id",
            name="fk_roles_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )
