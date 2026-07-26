"""Tenant workspace model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from security_system_database.models.types import UUID_TYPE

if TYPE_CHECKING:
    from security_system_database.models.company import Company


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Isolated workspace boundary for a customer company."""

    __tablename__ = "tenants"
    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="slug_lowercase"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'pending_setup')",
            name="status_valid",
        ),
        UniqueConstraint("company_id", name="uq_tenants_company_id"),
        UniqueConstraint("slug", name="uq_tenants_slug"),
        Index("ix_tenants_status", "status"),
    )

    company_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'pending_setup'"),
        nullable=False,
    )

    company: Mapped[Company] = relationship(
        "Company",
        back_populates="tenant",
    )
