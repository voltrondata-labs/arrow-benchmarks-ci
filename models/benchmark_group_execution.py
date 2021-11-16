import sqlalchemy as s
from sqlalchemy.dialects import postgresql

from db import Base
from models.base import BaseMixin, NotNull, Nullable
from models.run import Run
from utils import UnauthorizedException


class BenchmarkGroupExecution(Base, BaseMixin):
    __tablename__ = "benchmark_group_execution"
    id = NotNull(s.String, primary_key=True)
    lang = NotNull(s.String)
    name = NotNull(s.String)
    options = Nullable(s.String)
    flags = Nullable(postgresql.JSONB)
    benchmarkable_id = Nullable(s.String)
    run_id = Nullable(s.String)
    run_name = Nullable(s.String)
    machine = Nullable(s.String)
    process_pid = NotNull(s.Integer)
    command = Nullable(s.String)
    started_at = Nullable(s.DateTime(timezone=False))
    finished_at = Nullable(s.DateTime(timezone=False))
    total_run_time = Nullable(s.Interval)
    failed = Nullable(s.Boolean)
    return_code = Nullable(s.Integer)
    stderr = Nullable(s.Text)
    total_machine_virtual_memory = Nullable(s.BigInteger)
    created_at = NotNull(s.DateTime(timezone=False), server_default=s.sql.func.now())

    @classmethod
    def validate_data(cls, current_machine, data):
        if not Run.first(id=data["run_id"], machine_name=current_machine.name):
            raise UnauthorizedException
