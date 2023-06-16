import dataclasses
import os
from datetime import datetime
from typing import Optional, Union

import requests
import sqlalchemy as s
from benchalerts import AlertPipeline
from benchalerts import pipeline_steps as steps
from benchalerts.conbench_dataclasses import FullComparisonInfo
from benchalerts.integrations.github import GitHubRepoClient
from benchclients.conbench import LegacyConbenchClient
from benchclients.logging import log as benchalerts_log
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from integrations import adapter
from logger import log
from models.base import BaseMixin
from utils import generate_uuid


class BenchalertsRun(Base, BaseMixin):
    __tablename__ = "benchalerts_run"

    id: Mapped[str] = mapped_column(
        s.String, primary_key=True, default=generate_uuid, nullable=False
    )
    benchmarkable_id: Mapped[str] = mapped_column(
        s.String, s.ForeignKey("benchmarkable.id"), nullable=False
    )
    # Possibilities: <repo>-commit, pull-request, pyarrow-apache-wheel
    reason: Mapped[str] = mapped_column(s.String, nullable=False)

    finished_at: Mapped[Optional[datetime]] = mapped_column(
        s.DateTime(timezone=False), nullable=True
    )
    output: Mapped[Optional[Union[dict, list]]] = mapped_column(
        postgresql.JSONB, nullable=True
    )
    status: Mapped[Optional[str]] = mapped_column(s.String, nullable=True)
    check_link: Mapped[Optional[str]] = mapped_column(s.String, nullable=True)

    @property
    def ready_to_run(self) -> bool:
        """Whether all the runs have finished and we're ready to analyze the results."""
        return self.benchmarkable.all_runs_with_publishable_benchmark_results_finished() and (
            not self.benchmarkable.baseline
            or self.benchmarkable.baseline.all_runs_with_publishable_benchmark_results_finished()
        )

    def run_benchalerts(self) -> None:
        """Run a benchalerts pipeline to find possible errors/regressions and post
        about them in a GitHub Check and PR comment. Then mark this run as finished.
        """
        if self.reason.endswith("-wheel"):
            # No alerting on wheels for now.
            log.info(
                f"Skipping benchalerts for {self.benchmarkable_id} because it's a wheel"
            )
            self.mark_finished(comparison=None, check_link=None)
            return

        # For all other reasons, the benchmarkable ID is the commit hash
        commit_hash = self.benchmarkable_id

        # ...and the PR number should be populated, unless it's a merge-commit and
        # something went wrong finding the associated PR
        pr_number: Optional[int] = self.benchmarkable.pull_number
        if not pr_number:
            log.warning(f"Skipping benchalerts for {commit_hash}: no PR number found")
            self.mark_finished(comparison=None, check_link=None)
            return

        if self.reason == "pull-request":
            # Compare against the default-branch commit from which the PR was forked
            baseline_run_type = steps.BaselineRunCandidates.fork_point
        else:
            # Compare against the parent commit of the merge-commit
            baseline_run_type = steps.BaselineRunCandidates.parent

        # During pytest we want to mock the HTTP APIs
        if os.getenv("GITHUB_API_BASE_URL", "").startswith(
            "http://mocked-integrations"
        ):
            log.info("Using mocked integrations")
            conbench_client = LegacyConbenchClient(adapter=adapter)
            conbench_client.session.mount("http://", adapter)
            github_client = MockBenchalertsGitHubClient()
        else:
            conbench_client = None
            github_client = None

        run_ids = [
            run.id
            for run in self.benchmarkable.runs
            if run.machine_name not in ["test-mac-arm"]
        ]
        log.info(f"Analyzing run IDs: {run_ids}")
        benchalerts_log.setLevel("DEBUG")

        pipeline = AlertPipeline(
            steps=[
                steps.GetConbenchZComparisonForRunsStep(
                    run_ids=run_ids,
                    baseline_run_type=baseline_run_type,
                    z_score_threshold=30,
                    step_name="z_comparison",
                    conbench_client=conbench_client,
                ),
                steps.GitHubCheckStep(
                    commit_hash=commit_hash,
                    comparison_step_name="z_comparison",
                    repo=self.benchmarkable.repo,
                    github_client=github_client,
                ),
                steps.GitHubPRCommentAboutCheckStep(
                    pr_number=pr_number,
                    repo=self.benchmarkable.repo,
                    github_client=github_client,
                ),
                # TODO: post to Slack about failures, create GitHub issues?
            ]
        )

        output = pipeline.run_pipeline()
        self.mark_finished(
            comparison=output["z_comparison"],
            check_link=output["GitHubCheckStep"][0]["html_url"],
        )

    def mark_finished(
        self, comparison: Optional[FullComparisonInfo], check_link: Optional[str]
    ) -> None:
        """Mark this run as finished, and save the comparison data."""
        if comparison:
            self.output = dataclasses.asdict(comparison)
            self.status = steps.GitHubCheckStep._default_check_status(comparison).value
        if check_link:
            self.check_link = check_link

        self.finished_at = s.sql.func.now()
        self.save()


class MockBenchalertsGitHubClient(GitHubRepoClient):
    """During pytest, bypass the hassle of mocking the GitHub App login."""

    def __init__(self):
        self._is_github_app_token = True
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.base_url = os.environ["GITHUB_API_BASE_URL"] + "/repos/apache/arrow"
