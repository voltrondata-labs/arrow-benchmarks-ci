import socket
from copy import deepcopy
from datetime import datetime

import sqlalchemy as s
from authlib.jose import jwt
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import backref, relationship

from buildkite.benchmark.run import MockRun, repos_with_benchmark_groups
from config import Config
from db import Base
from integrations.buildkite import buildkite
from logger import log
from models.base import BaseMixin, NotNull, Nullable


class Machine(Base, BaseMixin):
    __tablename__ = "machine"
    name = NotNull(s.String, primary_key=True)
    info = Nullable(s.String)
    default_filters = NotNull(postgresql.JSONB)
    supported_filters = NotNull(postgresql.ARRAY(s.String))
    offline_warning_enabled = NotNull(s.Boolean, server_default="false")
    publish_benchmark_results = NotNull(s.Boolean, server_default="false")
    hostname = Nullable(s.String)
    ip_address = Nullable(s.String)
    port = Nullable(s.Integer)
    runs = relationship("Run", backref=backref("machine", lazy="joined"))

    @property
    def buildkite_pipeline_name(self):
        return f"Arrow BCI Benchmark on {self.name}"

    @property
    def buildkite_agent_queue(self):
        return f"{self.name}"

    @property
    def supported_langs(self):
        return sorted(list(self.default_filters["arrow-commit"]["langs"].keys()))

    def create_benchmark_pipeline(self):
        buildkite.create_pipeline(
            self.buildkite_pipeline_name, self.buildkite_agent_queue
        )

    def delete_benchmark_pipeline(self):
        buildkite.delete_pipeline(self.buildkite_pipeline_name)

    def run_filters_and_skip_reason(self, benchmarkable_type, override_filters=None):
        if benchmarkable_type not in self.default_filters:
            return (
                {},
                f"Benchmarking of {benchmarkable_type}s is not supported on {self.name}",
            )

        machine_run_filters = deepcopy(self.default_filters[benchmarkable_type])

        if not override_filters:
            return machine_run_filters, None

        if (
            "lang" in override_filters
            and override_filters["lang"] not in self.supported_langs
        ):
            return (
                override_filters,
                f"Only {self.supported_langs} langs are supported on {self.name}",
            )

        for override_filter in override_filters.keys():
            if override_filter not in self.supported_filters:
                return (
                    override_filters,
                    f"Only {self.supported_filters} filters are supported on {self.name}",
                )

        # Apply override_filters to machine_run_filters
        # override_filters can only have lang, name, command and flags filters
        if "command" in override_filters and "C++" in self.supported_langs:
            return override_filters, None

        if "lang" in override_filters:
            for lang in list(machine_run_filters["langs"].keys()):
                if lang != override_filters["lang"]:
                    machine_run_filters["langs"].pop(lang)

        if "name" in override_filters:
            benchmark_name = override_filters["name"]
            for lang in machine_run_filters["langs"].keys():
                benchmark_names = machine_run_filters["langs"][lang]["names"]
                if benchmark_name[-1] == "*":
                    filtered_benchmark_names = [
                        name
                        for name in benchmark_names
                        if name.startswith(benchmark_name[:-1])
                    ]
                else:
                    filtered_benchmark_names = [
                        name for name in benchmark_names if name == benchmark_name
                    ]
                machine_run_filters["langs"][lang]["names"] = filtered_benchmark_names

        for repo_with_benchmark_groups in repos_with_benchmark_groups:
            mock_run = MockRun(repo_with_benchmark_groups, filters=machine_run_filters)
            if not mock_run.has_benchmark_groups_to_execute():
                return (
                    machine_run_filters,
                    f"Provided benchmark filters do not have any benchmark groups to be executed on {self.machine}",
                )

        return machine_run_filters, None

    def has_scheduled_or_running_builds(self):
        return len(buildkite.get_scheduled_builds(self.buildkite_pipeline_name)) > 0

    def is_reachable(self):
        socket_timeout = 5

        for address in [self.ip_address, self.hostname]:
            if not address:
                continue

            socket.setdefaulttimeout(socket_timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((address, self.port))
                return True
            except socket.error as e:
                log.error(
                    f"Could not connect to {address} on port {self.port} because of {e}"
                )
                return False
            finally:
                s.close()

    def create_api_access_token(self):
        header = {"alg": "HS256"}
        payload = {"machine": self.name, "created_at": str(datetime.utcnow())}
        key = Config.SECRET
        return jwt.encode(header, payload, key).decode()
