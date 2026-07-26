"""Add-on module assignment model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from security_system_database.base import Base
from security_system_database.models.mixins import UUIDPrimaryKeyMixin
from security_system_database.models.types import DATETIME_TIMEZONE, UUID_TYPE


class AddOnModule(Base, UUIDPrimaryKeyMixin):
    """Assignment of a catalog module to an add-on."""

    __tablename__ = "add_on_modules"
    __table_args__ = (
        UniqueConstraint(
            "add_on_id",
            "module_id",
            name="uq_add_on_modules_add_on_module",
        ),
        Index("ix_add_on_modules_add_on_id", "add_on_id"),
        Index("ix_add_on_modules_module_id", "module_id"),
    )

    add_on_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "add_ons.id",
            name="fk_add_on_modules_add_on_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    module_id: Mapped[UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey(
            "modules.id",
            name="fk_add_on_modules_module_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DATETIME_TIMEZONE,
        server_default=func.now(),
        nullable=False,
    )
