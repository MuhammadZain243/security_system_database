"""Company add-on assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class CompanyAddOn(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Add-on assigned to a customer company."""

    __tablename__ = "company_add_ons"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'cancelled', 'expired', 'suspended')",
            name="status_valid",
        ),
        Index("ix_company_add_ons_add_on_id", "add_on_id"),
        Index("ix_company_add_ons_company_id", "company_id"),
        Index("ix_company_add_ons_status", "status"),
        Index(
            "uq_company_add_ons_one_active_per_company_add_on",
            "company_id",
            "add_on_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    company_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "companies.id",
            name="fk_company_add_ons_company_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    add_on_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "add_ons.id",
            name="fk_company_add_ons_add_on_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DATETIME_TIMEZONE, nullable=False)
    current_period_starts_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    current_period_ends_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
