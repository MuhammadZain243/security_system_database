"""Customer company model."""

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
    from security_system_database.models.tenant import Tenant


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Customer company managed from the platform admin area."""

    __tablename__ = "companies"
    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="slug_lowercase"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'pending_onboarding')",
            name="status_valid",
        ),
        UniqueConstraint("slug", name="uq_companies_slug"),
        Index("ix_companies_email", "email"),
        Index("ix_companies_status", "status"),
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'pending_onboarding'"),
        nullable=False,
    )

    tenant: Mapped[Tenant | None] = relationship(
        "Tenant",
        back_populates="company",
        uselist=False,
    )
