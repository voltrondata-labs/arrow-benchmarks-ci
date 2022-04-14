import sqlalchemy as s
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import backref, relationship

from config import Config
from db import Base, Session
from integrations import IntegrationException
from integrations.conbench import conbench
from logger import log
from models.base import BaseMixin, NotNull, Nullable
from models.machine import Machine
from models.notification import Notification
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
    notifications = relationship(
        "Notification", backref=backref("benchmarkable", lazy="joined")
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
    def displayable_message(self):
        if self.is_commit():
            return self.data["commit"]["message"].splitlines()[0][:60]

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
            benchmarkable.add_notifications()

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
                self.type, override_filters
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

    def add_notifications(self):
        self.notifications.append(Notification(type="slack_message"))
        if self.pull_number:
            self.notifications.append(Notification(type="pull_comment"))
            self.notifications.append(Notification(type="pull_comment_alert"))

    @property
    def runs_with_buildkite_builds_and_publishable_benchmark_results(self):
        return sorted(
            [
                run
                for run in self.runs
                if run.buildkite_data and run.machine.publish_benchmark_results
            ],
            key=lambda x: x.machine.name,
        )

    def machine_run(self, machine):
        for run in self.runs:
            if run.machine == machine:
                return run

    def baseline_machine_run(self, machine):
        for run in self.baseline.runs:
            if run.machine == machine:
                return run

    def conbench_compare_runs_web_url(self, machine):
        baseline_run_id = self.baseline_machine_run(machine).id
        run_id = self.machine_run(machine).id
        return f"{Config.CONBENCH_URL}/compare/runs/{baseline_run_id}...{run_id}/"

    def machine_runs_status(self, machine):
        run = self.machine_run(machine)
        baseline_run = self.baseline_machine_run(machine)

        if run.status == "skipped":
            return f"Skipped :warning: {run.skip_reason}"

        if run.finished_at and baseline_run.finished_at:
            try:
                regressions, improvements = self.regressions_and_improvements(machine)
                if run.status == "finished" and baseline_run.status == "finished":
                    runs_status = (
                        f"Finished :arrow_down:{regressions}% :arrow_up:{improvements}%"
                    )
                else:
                    runs_status = (
                        f"Failed :arrow_down:{regressions}% :arrow_up:{improvements}%"
                    )

                if not run.context_matches_baseline_run_context():
                    runs_status += (
                        f" :warning: Contender and baseline run contexts do not match"
                    )

                return runs_status
            except IntegrationException:
                return "Failed"
            except Exception as e:
                raise e

        runs_status = "Scheduled"
        if (
            machine.offline_warning_enabled
            and (machine.hostname or machine.ip_address)
            and not machine.is_reachable()
        ):
            runs_status += f" :warning: {machine.name} is offline."
        return runs_status

    def all_runs_with_publishable_benchmark_results_finished(self):
        return all(
            [
                run.finished_at
                for run in self.runs
                if run.machine.publish_benchmark_results
            ]
        )

    def slack_notification(self):
        for notification in self.notifications:
            if notification.type == "slack_message":
                return notification

    def pull_notification(self):
        for notification in self.notifications:
            if notification.type == "pull_comment":
                return notification

    def get_conbench_compare_results(self, machine):
        return conbench.get_compare_runs(
            self.baseline_machine_run(machine).id,
            self.machine_run(machine).id,
        )

    def regressions_and_improvements(self, machine):
        results = self.get_conbench_compare_results(machine)

        if len(results) == 0:
            return 0, 0

        regressions = round(
            len([r for r in results if r["contender_z_regression"]])
            / len(results)
            * 100,
            2,
        )
        improvements = round(
            len([r for r in results if r["contender_z_improvement"]])
            / len(results)
            * 100,
            2,
        )

        return regressions, improvements

    def has_high_level_of_regressions(self):
        for run in self.runs_with_buildkite_builds_and_publishable_benchmark_results:
            results = self.get_conbench_compare_results(run.machine)
            print(">>>>>>>results", results)

            # Filter results by Python and R benchmarks
            results = [r for r in results if r["language"] in ["Python", "R"]]
            if not results:
                continue

            # Check if run has at least one Python and R benchmark with z-score < -10.0
            if [r for r in results if r["contender_z_score"] < -10.0]:
                return True

            # Check if sum of all run's Python and R benchmarks z-scores < -200.00
            if sum([r for r in results if r["contender_z_score"] < 0]) < -200.00:
                return True

        return False
