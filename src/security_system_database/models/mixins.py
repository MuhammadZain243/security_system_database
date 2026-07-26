"""Reusable SQLAlchemy model mixins."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class UUIDPrimaryKeyMixin:
    """Mixin that provides a UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """Mixin that provides creation and update timestamps."""

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


class SoftDeleteMixin:
    """Mixin that provides a nullable soft-delete timestamp."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DATETIME_TIMEZONE,
        nullable=True,
    )


class TenantOwnershipMixin:
    """Mixin for tenant-owned tables."""

    tenant_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )

    @declared_attr.directive
    def __table_args__(cls: Any) -> tuple[Index]:
        return (Index(f"ix_{cls.__tablename__}_tenant_id", "tenant_id"),)


class AuditActorMixin:
    """Mixin that stores nullable actor identifiers for audit trails."""

    created_by_user_id: Mapped[UUID | None] = mapped_column(UUID_TYPE, nullable=True)
    updated_by_user_id: Mapped[UUID | None] = mapped_column(UUID_TYPE, nullable=True)
    deleted_by_user_id: Mapped[UUID | None] = mapped_column(UUID_TYPE, nullable=True)
