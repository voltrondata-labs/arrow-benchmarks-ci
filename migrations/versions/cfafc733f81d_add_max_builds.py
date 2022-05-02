"""add_max_builds

Revision ID: cfafc733f81d
Revises: 7d8a160a2fd1
Create Date: 2022-04-29 15:23:28.220573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cfafc733f81d"
down_revision = "7d8a160a2fd1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "machine",
        sa.Column("max_builds", sa.Integer(), server_default="1", nullable=True),
    )

    op.execute("UPDATE machine SET max_builds = 1")
    op.alter_column("machine", "max_builds", existing_type=sa.Integer, nullable=False)


def downgrade():
    op.drop_column("machine", "max_builds")
