"""verify ai access for user column

Revision ID: 0e68dc1847c5
Revises: 649a89238c39
Create Date: 2025-12-06 21:50:29.691871

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0e68dc1847c5"
down_revision: Union[str, Sequence[str], None] = "649a89238c39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user",
        sa.Column(
            "has_ai_access",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "user",
        "has_ai_access",
    )
