"""Tenant permission definition model."""

from sqlalchemy import CheckConstraint, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Permission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Global tenant permission definition assigned to tenant roles."""

    __tablename__ = "permissions"
    __table_args__ = (
        CheckConstraint("key = lower(key)", name="key_lowercase"),
        UniqueConstraint("key", name="uq_permissions_key"),
        Index("ix_permissions_category", "category"),
    )

    key: Mapped[str] = mapped_column(String(160), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
