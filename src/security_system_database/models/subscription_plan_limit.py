"""Subscription plan limit model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class SubscriptionPlanLimit(Base, UUIDPrimaryKeyMixin):
    """Practical usage limit attached to a subscription plan."""

    __tablename__ = "subscription_plan_limits"
    __table_args__ = (
        CheckConstraint(
            "limit_key IN ('max_team_members', 'max_storage_mb', 'max_custom_roles')",
            name="limit_key_valid",
        ),
        CheckConstraint("limit_value >= 0", name="limit_value_non_negative"),
        UniqueConstraint(
            "subscription_plan_id",
            "limit_key",
            name="uq_subscription_plan_limits_plan_key",
        ),
        Index("ix_subscription_plan_limits_limit_key", "limit_key"),
        Index(
            "ix_subscription_plan_limits_subscription_plan_id", "subscription_plan_id"
        ),
    )

    subscription_plan_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "subscription_plans.id",
            name="fk_subscription_plan_limits_plan_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    limit_key: Mapped[str] = mapped_column(String(80), nullable=False)
    limit_value: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
