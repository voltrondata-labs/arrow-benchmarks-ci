"""initial_schema

Revision ID: 4dee912a87fa
Revises: 
Create Date: 2021-10-19 17:08:20.360069

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4dee912a87fa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "benchmark_group_execution",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("lang", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("options", sa.String(), nullable=True),
        sa.Column("flags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("benchmarkable_id", sa.String(), nullable=True),
        sa.Column("run_id", sa.String(), nullable=True),
        sa.Column("run_name", sa.String(), nullable=True),
        sa.Column("machine", sa.String(), nullable=True),
        sa.Column("process_pid", sa.Integer(), nullable=False),
        sa.Column("command", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("total_run_time", sa.Interval(), nullable=True),
        sa.Column("failed", sa.Boolean(), nullable=True),
        sa.Column("return_code", sa.Integer(), nullable=True),
        sa.Column("stderr", sa.Text(), nullable=True),
        sa.Column("total_machine_virtual_memory", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "benchmarkable",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("baseline_id", sa.String(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("pull_number", sa.Integer(), nullable=True),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "machine",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("info", sa.String(), nullable=True),
        sa.Column(
            "default_filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("supported_filters", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("supported_langs", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column(
            "offline_warning_enabled",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column(
            "include_in_benchmark_results_messages",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("hostname", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "memory_usage",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("benchmark_group_execution_id", sa.String(), nullable=False),
        sa.Column("process_pid", sa.Integer(), nullable=False),
        sa.Column("parent_process_pid", sa.Integer(), nullable=False),
        sa.Column("process_name", sa.String(), nullable=False),
        sa.Column("process_cmdline", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("mem_rss_bytes", sa.BigInteger(), nullable=False),
        sa.Column("mem_percent", sa.Float(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notification",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("benchmarkable_id", sa.String(), nullable=False),
        sa.Column("message", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["benchmarkable_id"],
            ["benchmarkable.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "run",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("benchmarkable_id", sa.String(), nullable=False),
        sa.Column("machine", sa.String(), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("env", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "buildkite_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("status", sa.String(), server_default="created", nullable=False),
        sa.Column("skip_reason", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("total_run_time", sa.Interval(), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "machine_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("conda_packages", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["benchmarkable_id"],
            ["benchmarkable.id"],
        ),
        sa.ForeignKeyConstraint(
            ["machine"],
            ["machine.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("run")
    op.drop_table("notification")
    op.drop_table("memory_usage")
    op.drop_table("machine")
    op.drop_table("benchmarkable")
    op.drop_table("benchmark_group_execution")
    # ### end Alembic commands ###
