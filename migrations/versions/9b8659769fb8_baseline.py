"""baseline

Revision ID: 9b8659769fb8
Revises:
Create Date: 2026-07-25 21:06:01.758467

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "9b8659769fb8"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
