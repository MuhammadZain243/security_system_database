"""Company subscription assignment model."""

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


class CompanySubscription(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Subscription plan assigned to a customer company."""

    __tablename__ = "company_subscriptions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('trialing', 'active', 'past_due', 'cancelled', 'expired', 'suspended')",
            name="status_valid",
        ),
        Index("ix_company_subscriptions_company_id", "company_id"),
        Index("ix_company_subscriptions_subscription_plan_id", "subscription_plan_id"),
        Index("ix_company_subscriptions_status", "status"),
        Index(
            "uq_company_subscriptions_one_active_per_company",
            "company_id",
            unique=True,
            postgresql_where=text("status IN ('trialing', 'active')"),
        ),
    )

    company_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "companies.id",
            name="fk_company_subscriptions_company_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    subscription_plan_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "subscription_plans.id",
            name="fk_company_subscriptions_plan_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'active'"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DATETIME_TIMEZONE, nullable=False)
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )
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
