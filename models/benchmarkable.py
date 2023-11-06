import functools
import traceback
from typing import Optional

import sqlalchemy as s
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import backref, relationship

from config import Config
from db import Base, Session
from integrations import IntegrationException
from logger import log
from models.base import BaseMixin, NotNull, Nullable
from models.benchalerts_run import BenchalertsRun
from models.machine import Machine
from models.run import Run


class Benchmarkable(Base, BaseMixin):
    __tablename__ = "benchmarkable"
    id = NotNull(s.String, primary_key=True)  # commit sha or wheel
    type = NotNull(s.String)
    baseline_id = Nullable(s.String)
    data = Nullable(postgresql.JSONB)
    pull_number = Nullable(s.Integer)
    reason = NotNull(s.String)
    created_at = NotNull(s.DateTime(timezone=False), server_default=s.sql.func.now())
    runs = relationship("Run", backref=backref("benchmarkable", lazy="joined"))
    # Right now this is always 1-to-1, but leaving it as a list in case we add more
    # alerting runs per benchmarkable in the future.
    benchalerts_runs = relationship(
        "BenchalertsRun", backref=backref("benchmarkable", lazy="joined")
    )

    @property
    def baseline(self):
        return Benchmarkable.get(self.baseline_id)

    @property
    def displayable_id(self):
        if self.is_commit():
            return self.id[:8]
        return self.id

    @property
    def html_url(self):
        if self.is_commit():
            return self.data["html_url"]

    @property
    def committer(self):
        if self.is_commit():
            if self.data["committer"] is not None:
                return self.data["committer"]["login"]
            else:
                return self.data["commit"]["committer"]["name"]

    @property
    def committer_url(self):
        if self.is_commit():
            if self.data["committer"] is not None:
                return self.data["committer"]["html_url"]

    @property
    def displayable_message(self) -> Optional[str]:
        if self.is_commit():
            # Remove % since they cause JSON parsing issues when passed to buildkite.
            # TODO: are there other characters we should also check? And is it possible
            # to escape instead of deleting?
            return self.data["commit"]["message"].splitlines()[0][:60].replace("%", "")

    @property
    def slack_text(self):
        if self.is_commit():
            if self.data["committer"]:
                return (
                    f"<{self.html_url}|`{self.displayable_id}`> {self.displayable_message} "
                    f"[author: <{self.committer_url}|{self.committer}>]"
                )
            else:
                return (
                    f"<{self.html_url}|`{self.displayable_id}`> {self.displayable_message} "
                    f"[author: {self.committer}]"
                )

        return self.id

    @property
    def repo(self):
        for repo, params in Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS.items():
            if params["benchmarkable_type"] == self.type:
                return repo

    @property
    def repo_params(self):
        for repo, params in Config.GITHUB_REPOS_WITH_BENCHMARKABLE_COMMITS.items():
            if params["benchmarkable_type"] == self.type:
                return params

    def is_commit(self):
        return self.type.endswith("-commit")

    @classmethod
    def create(cls, data):
        benchmarkable = cls.get(data["id"])
        if benchmarkable:
            return benchmarkable

        try:
            override_filters = data.pop("filters", None)

            benchmarkable = cls(**data)
            benchmarkable.add_runs(override_filters, data["reason"])
            benchmarkable.add_benchalerts_run(reason=data["reason"])

            Session.add(benchmarkable)
            Session.commit()

            log.info(f"Inserted {benchmarkable}")
            return benchmarkable
        except Exception as e:
            Session.rollback()
            raise e

    def add_runs(self, override_filters, reason):
        for machine in Machine.all():
            filters, skip_reason = machine.run_filters_and_skip_reason(
                benchmarkable_type=self.type,
                benchmarkable_reason=reason,
                benchmarkable_commit_msg=self.displayable_message,
                override_filters=override_filters,
            )
            self.runs.append(
                Run(
                    machine_name=machine.name,
                    filters=filters,
                    reason=reason,
                    status="skipped" if skip_reason else "created",
                    skip_reason=skip_reason,
                    finished_at=s.sql.func.now() if skip_reason else None,
                )
            )

    def add_benchalerts_run(self, reason: str):
        if (
            self.pull_number
            and self.repo_params["publish_benchmark_results_on_pull_requests"]
        ):
            self.benchalerts_runs.append(BenchalertsRun(reason=reason))

    def all_runs_with_publishable_benchmark_results_finished(self):
        return all(
            [
                run.finished_at
                for run in self.runs
                if run.machine.publish_benchmark_results
            ]
        )
