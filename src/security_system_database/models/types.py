"""Shared SQLAlchemy type conventions."""

from typing import Annotated
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import mapped_column

UUID_TYPE = PostgreSQLUUID(as_uuid=True)
DATETIME_TIMEZONE = DateTime(timezone=True)

ShortString = Annotated[str, mapped_column(String(255))]
UUIDColumn = Annotated[UUID, mapped_column(UUID_TYPE)]
