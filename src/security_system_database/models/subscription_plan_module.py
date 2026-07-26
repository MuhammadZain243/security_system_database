"""Subscription plan module assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class SubscriptionPlanModule(Base, UUIDPrimaryKeyMixin):
    """Assignment of a catalog module to a subscription plan."""

    __tablename__ = "subscription_plan_modules"
    __table_args__ = (
        UniqueConstraint(
            "subscription_plan_id",
            "module_id",
            name="uq_subscription_plan_modules_plan_module",
        ),
        Index("ix_subscription_plan_modules_module_id", "module_id"),
        Index(
            "ix_subscription_plan_modules_subscription_plan_id", "subscription_plan_id"
        ),
    )

    subscription_plan_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "subscription_plans.id",
            name="fk_subscription_plan_modules_plan_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    module_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "modules.id",
            name="fk_subscription_plan_modules_module_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
