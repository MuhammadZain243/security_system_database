"""Subscription plan model."""

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class SubscriptionPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Platform-created subscription plan for customer companies."""

    __tablename__ = "subscription_plans"
    __table_args__ = (
        CheckConstraint("slug = lower(slug)", name="slug_lowercase"),
        CheckConstraint("currency = upper(currency)", name="currency_uppercase"),
        CheckConstraint("length(currency) = 3", name="currency_length_valid"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'archived')",
            name="status_valid",
        ),
        CheckConstraint(
            "billing_interval IN ('monthly', 'yearly', 'one_time')",
            name="billing_interval_valid",
        ),
        CheckConstraint("price_amount >= 0", name="price_amount_non_negative"),
        CheckConstraint("trial_days >= 0", name="trial_days_non_negative"),
        UniqueConstraint("slug", name="uq_subscription_plans_slug"),
        Index("ix_subscription_plans_billing_interval", "billing_interval"),
        Index("ix_subscription_plans_status", "status"),
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        server_default=text("'active'"),
        nullable=False,
    )
    billing_interval: Mapped[str] = mapped_column(String(32), nullable=False)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    trial_days: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0"),
        nullable=False,
    )
