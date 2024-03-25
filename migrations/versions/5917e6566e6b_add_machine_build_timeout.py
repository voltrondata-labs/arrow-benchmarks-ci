"""add machine build_timeout

Revision ID: 5917e6566e6b
Revises: c30e58775d47
Create Date: 2024-03-25 14:41:06.064070

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5917e6566e6b"
down_revision = "c30e58775d47"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("machine", sa.Column("build_timeout", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("machine", "build_timeout")
