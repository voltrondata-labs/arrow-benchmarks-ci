"""no_warnings

Revision ID: 42365abd2377
Revises: 5917e6566e6b
Create Date: 2024-06-17 10:27:48.844765

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "42365abd2377"
down_revision = "5917e6566e6b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("machine", "hostname")
    op.drop_column("machine", "ip_address")
    op.drop_column("machine", "port")
    op.drop_column("machine", "offline_warning_enabled")


def downgrade():
    op.add_column(
        "machine",
        sa.Column(
            "offline_warning_enabled",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "machine", sa.Column("port", sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "machine",
        sa.Column("ip_address", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "machine",
        sa.Column("hostname", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
