import sqlalchemy as s
from sqlalchemy.dialects import postgresql

from db import Base
from models.base import BaseMixin, NotNull, Nullable
from models.benchmark_group_execution import BenchmarkGroupExecution
from models.run import Run
from utils import UnauthorizedException


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

    @classmethod
    def validate_data(cls, current_machine, data):
        benchmark_group_execution = BenchmarkGroupExecution.get(
            data["benchmark_group_execution_id"]
        )
        if not benchmark_group_execution:
            raise UnauthorizedException

        if not Run.first(
            id=benchmark_group_execution.run_id, machine_name=current_machine.name
        ):
            raise UnauthorizedException
