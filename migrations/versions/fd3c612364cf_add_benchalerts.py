"""add benchalerts

Revision ID: fd3c612364cf
Revises: cfafc733f81d
Create Date: 2023-06-12 13:04:56.343773

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fd3c612364cf"
down_revision = "cfafc733f81d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "benchalerts_run",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("benchmarkable_id", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["benchmarkable_id"],
            ["benchmarkable.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("notification")


def downgrade():
    op.create_table(
        "notification",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("type", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "benchmarkable_id", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "message",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "finished_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["benchmarkable_id"],
            ["benchmarkable.id"],
            name="notification_benchmarkable_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="notification_pkey"),
    )
    op.drop_table("benchalerts_run")
