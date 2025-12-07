"""create token blacklist table

Revision ID: f53fe47831c5
Revises:
Create Date: 2025-12-06 11:33:40.616061

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f53fe47831c5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tokenblacklist",
        sa.Column("token", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("token"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table(
        "tokenblacklist",
        if_exists=True,
    )
