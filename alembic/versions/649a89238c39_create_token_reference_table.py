"""create Token Reference table

Revision ID: 649a89238c39
Revises: f53fe47831c5
Create Date: 2025-12-06 12:32:56.751458

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "649a89238c39"
down_revision: Union[str, Sequence[str], None] = "f53fe47831c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "token_reference",
        sa.Column("access_token", sa.String(), primary_key=True),
        sa.Column("refresh_token", sa.String(), primary_key=True),
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(
        "token_reference",
        if_exists=True,
    )
