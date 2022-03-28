import sqlalchemy as s
from sqlalchemy.dialects import postgresql

from db import Base
from integrations.github import Github
from integrations.slack import slack
from logger import log
from models.base import BaseMixin, NotNull, Nullable
from models.machine import Machine
from utils import generate_uuid


def supported_benchmarks_info():
    comment = "Supported benchmarks:\n"
    for machine in Machine.all(None, order_by="name", publish_benchmark_results=True):
        comment += f"{machine.name}: {machine.info}\n"

    return comment


class Notification(Base, BaseMixin):
    __tablename__ = "notification"
    id = NotNull(s.String, primary_key=True, default=generate_uuid)
    type = NotNull(s.String)  # slack_message or pull_comment
    benchmarkable_id = NotNull(s.String, s.ForeignKey("benchmarkable.id"))
    message = Nullable(postgresql.JSONB)
    finished_at = Nullable(s.DateTime(timezone=False))

    @property
    def pull_comment_body(self):
        if self.message:
            return self.message["body"]

    @property
    def pull_comment_url(self):
        return self.message["url"]

    @property
    def pull_number(self):
        return self.benchmarkable.pull_number

    def all_runs_with_publishable_benchmark_results_finished(self):
        return (
            self.benchmarkable.all_runs_with_publishable_benchmark_results_finished()
            and self.benchmarkable.baseline is not None
            and self.benchmarkable.baseline.all_runs_with_publishable_benchmark_results_finished()
        )

    def generate_comment_with_compare_runs_links(self):
        comment = f"Conbench compare runs links:\n"
        for machine in Machine.all(
            None, order_by="name", publish_benchmark_results=True
        ):
            if not self.benchmarkable.machine_run(
                machine
            ) and not self.benchmarkable.baseline_machine_run(machine):
                continue

            status = self.benchmarkable.machine_runs_status(machine)
            url = self.benchmarkable.conbench_compare_runs_web_url(machine)
            if self.type == "slack_message":
                comment += f"[{status}] <{url}|{machine.name}>\n"
            else:
                comment += f"[{status}] [{machine.name}]({url})\n"
        return comment

    def generate_pull_comment_body(self):
        comment = (
            f"Benchmark runs are scheduled for baseline = {self.benchmarkable.baseline_id} "
            f"and contender = {self.benchmarkable.id}. "
        )

        # Add extra explanation when posting benchmark results for arrow master commit
        # into its originating PR.
        if self.benchmarkable.reason.endswith("-commit"):
            comment += (
                f"{self.benchmarkable.id} is a master commit associated with this PR. "
            )

        comment += (
            f"Results will be available as each benchmark for each run completes.\n"
        )

        return (
            comment
            + self.generate_comment_with_compare_runs_links()
            + supported_benchmarks_info()
        )

    def generate_slack_message_text(self):
        # Specify baseline and contender benchmarkables (shas or wheels)
        text = (
            f"Benchmark results for {self.benchmarkable.runs[0].buildkite_run_name}\n"
            f"contender {self.benchmarkable.slack_text}\n"
            f"baseline {self.benchmarkable.baseline.slack_text}:\n"
        )
        return (
            text
            + self.generate_comment_with_compare_runs_links()
            + self.generate_text_with_buildkite_build_urls()
        )

    def generate_text_with_buildkite_build_urls(self):
        text = f"Buildkite builds:\n"
        for run in (
            self.benchmarkable.runs_with_buildkite_builds_and_publishable_benchmark_results
            + self.benchmarkable.baseline.runs_with_buildkite_builds_and_publishable_benchmark_results
        ):
            text += f"{run.buildkite_build_web_url_with_status}\n"

        return text

    def create_pull_comment(self, comment_body):
        log.info(
            f"Creating pull comment for pull {self.pull_number} {self.benchmarkable.type} {self.benchmarkable_id}"
        )
        self.message = Github(self.benchmarkable.repo).create_pull_comment(
            self.pull_number, comment_body
        )
        self.save()

    def update_pull_comment(self, comment_body):
        log.info(
            f"Updating pull comment for pull {self.pull_number} {self.benchmarkable.type} {self.benchmarkable_id}"
        )
        self.message = Github(self.benchmarkable.repo).update_pull_comment(
            self.pull_comment_url, comment_body
        )
        self.save()

    def post_slack_message(self, text):
        log.info(
            f"Posting slack message for {self.benchmarkable.type} {self.benchmarkable_id}"
        )
        self.message = slack.post_message(text)
        self.save()

    def mark_finished(self):
        self.finished_at = s.sql.func.now()
        self.save()
