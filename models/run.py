import json
from datetime import datetime

import sqlalchemy as s
from sqlalchemy.dialects import postgresql

from config import Config
from db import Base
from integrations.buildkite import buildkite
from logger import log
from models.base import BaseMixin, NotNull, Nullable
from utils import generate_uuid


class Run(Base, BaseMixin):
    __tablename__ = "run"
    id = NotNull(s.String, primary_key=True, default=generate_uuid)
    benchmarkable_id = NotNull(s.String, s.ForeignKey("benchmarkable.id"))
    machine_name = NotNull("machine", s.String, s.ForeignKey("machine.name"))
    filters = NotNull(postgresql.JSONB)
    reason = NotNull(s.String)
    env = Nullable(postgresql.JSONB)
    buildkite_data = Nullable(postgresql.JSONB)
    status = NotNull(
        s.String, server_default="created"
    )  # created, scheduled, finished, failed, skipped
    skip_reason = Nullable(s.String)
    created_at = NotNull(s.DateTime(timezone=False), server_default=s.sql.func.now())
    scheduled_at = Nullable(s.DateTime(timezone=False))
    finished_at = Nullable(s.DateTime(timezone=False))
    total_run_time = Nullable(s.Interval)

    context = Nullable(postgresql.JSONB)
    machine_info = Nullable(postgresql.JSONB)
    conda_packages = Nullable(s.Text)

    @property
    def buildkite_build_message(self):
        pull_request_info = (
            f"#{self.benchmarkable.pull_number}"
            if self.reason == "pull-request"
            else ""
        )
        return (
            f"{self.benchmarkable.type} {self.benchmarkable.id} reason = {self.reason} {pull_request_info} "
            f"filters = {self.filters} message {self.benchmarkable.displayable_message} "
            f"timestamp={self.benchmarkable.created_at}"
        )

    @property
    def buildkite_build_url(self):
        return self.buildkite_data.get("url")

    @property
    def buildkite_build_web_url(self):
        if self.buildkite_data:
            return self.buildkite_data.get("web_url")

    def buildkite_build_web_url_with_status(self, format):
        if format == "slack_message":
            return (
                f"[{self.status.capitalize()}] <{self.buildkite_build_web_url}| "
                f"`{self.benchmarkable.displayable_id}` {self.machine_name}>"
            )

        return (
            f"[{self.status.capitalize()}] "
            f"[`{self.benchmarkable.displayable_id}` {self.machine_name}]({self.buildkite_build_web_url})"
        )

    @property
    def buildkite_build_run_time(self):
        if self.buildkite_data.get("started_at") and self.buildkite_data.get(
            "finished_at"
        ):
            return datetime.strptime(
                self.buildkite_data["finished_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) - datetime.strptime(
                self.buildkite_data["started_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )

    @property
    def buildkite_build_run_time_until_now(self):
        if self.buildkite_data.get("started_at"):
            return datetime.utcnow() - datetime.strptime(
                self.buildkite_data["started_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )

    @property
    def buildkite_run_name(self):
        if self.reason.endswith("-commit"):
            return f"commit: {self.benchmarkable_id}"
        if self.reason == "pull-request":
            return f"pull request: {self.benchmarkable.pull_number}"

        return f"{self.benchmarkable.type}: {self.benchmarkable_id}"

    @property
    def conbench_run_reason(self):
        if self.reason.endswith("-commit"):
            return "commit"
        if self.reason == "pull-request":
            return "pull request"

        return self.reason

    def create_benchmark_build(self):
        if self.benchmarkable.pull_number and self.reason == "pull-request":
            pr_number = str(self.benchmarkable.pull_number)
        else:
            pr_number = ""

        env = {
            "BENCHMARKABLE": self.benchmarkable_id,
            "BENCHMARKABLE_TYPE": self.benchmarkable.type,
            "BENCHMARKABLE_PR_NUMBER": pr_number,
            "BUILD_TIMEOUT": self.machine.build_timeout,
            "FILTERS": json.dumps(self.filters),
            "MACHINE": self.machine_name,
            "RUN_ID": self.id,
            "RUN_NAME": self.buildkite_run_name,
            "RUN_REASON": self.conbench_run_reason,
            "PYTHON_VERSION": Config.PYTHON_VERSION_FOR_BENCHMARK_BUILDS,
        }

        self.buildkite_data = buildkite.create_build(
            pipeline_name=self.machine.buildkite_pipeline_name,
            commit="HEAD",
            branch="main",
            message=self.buildkite_build_message,
            env=env,
        )

        self.env = env
        self.status = "scheduled"
        self.scheduled_at = s.sql.func.now()
        self.save()

    def update_buildkite_data(self):
        data = buildkite.get_build(self.buildkite_build_url)
        self.buildkite_data = data
        self.save()

    def mark_finished(self):
        # buildkite/benchmarks/pipeline.yml > "Pipeline upload" step  = self.buildkite_data["jobs"][0]
        # buildkite/benchmarks/pipeline.yml > "Run Benchmarks" step = self.buildkite_data["jobs"][1]
        for job in self.buildkite_data["jobs"]:
            if job["state"] in ["scheduled", "running", "assigned", "accepted"]:
                return

        self.finished_at = self.buildkite_data["finished_at"]
        self.total_run_time = self.buildkite_build_run_time

        if (
            len(self.buildkite_data["jobs"]) > 1
            and self.buildkite_data["jobs"][1]["state"] == "passed"
        ):
            log.info(
                f"Marking run for benchmarkable_id = {self.benchmarkable_id} and machine = {self.machine_name} as finished"
            )
            self.status = "finished"
        else:
            log.info(
                f"Marking run for benchmarkable_id = {self.benchmarkable_id} and machine = {self.machine_name} as failed"
            )
            self.status = "failed"

        self.save()

    def context_matches_baseline_run_context(self):
        baseline_run = self.benchmarkable.baseline_machine_run(self.machine)
        return (
            self.context == baseline_run.context
            and self.machine_info == baseline_run.machine_info
        )
