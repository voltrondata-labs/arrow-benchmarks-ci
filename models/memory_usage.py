import sqlalchemy as s
from sqlalchemy.dialects import postgresql

from db import Base
from models.base import BaseMixin, NotNull, Nullable


class MemoryUsage(Base, BaseMixin):
    __tablename__ = "memory_usage"
    id = NotNull(s.String, primary_key=True)
    benchmark_group_execution_id = NotNull(s.String)
    process_pid = NotNull(s.Integer)
    parent_process_pid = NotNull(s.Integer)
    process_name = NotNull(s.String)
    process_cmdline = Nullable(postgresql.ARRAY(s.String))
    mem_rss_bytes = NotNull(s.BigInteger)
    mem_percent = Nullable(s.Float)
    created_at = NotNull(s.DateTime(timezone=False), server_default=s.sql.func.now())
