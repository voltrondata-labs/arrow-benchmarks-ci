"""pr_comment_link

Revision ID: c30e58775d47
Revises: fd3c612364cf
Create Date: 2023-10-02 12:46:03.070179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c30e58775d47"
down_revision = "fd3c612364cf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "benchalerts_run", sa.Column("pr_comment_link", sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column("benchalerts_run", "pr_comment_link")
