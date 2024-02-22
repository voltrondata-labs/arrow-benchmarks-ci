import dataclasses
import os
from copy import deepcopy
from datetime import datetime
from typing import Optional, Tuple, Union

import requests
import sqlalchemy as s
from benchalerts import Alerter, AlertPipeline
from benchalerts import pipeline_steps as steps
from benchalerts.conbench_dataclasses import FullComparisonInfo
from benchalerts.integrations.github import CheckStatus, GitHubRepoClient
from benchalerts.message_formatting import _list_results
from benchclients.conbench import ConbenchClient
from benchclients.logging import log as benchalerts_log
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from integrations import adapter
from logger import log
from models.base import BaseMixin
from utils import generate_uuid

MACHINES_WITH_PUBLIC_BK_URLS = [
    "ec2-t3-xlarge-us-east-2",
    "test-mac-arm",
    "ursa-i9-9960x",
    "ursa-thinkcentre-m75q",
]


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
    pr_comment_link: Mapped[Optional[str]] = mapped_column(s.String, nullable=True)

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
            self.mark_finished(comparison=None, check_link=None, pr_comment_link=None)
            return

        # For all other reasons, the benchmarkable ID is the commit hash
        commit_hash = self.benchmarkable_id

        # ...and the PR number should be populated, unless it's a merge-commit and
        # something went wrong finding the associated PR
        pr_number: Optional[int] = self.benchmarkable.pull_number
        if not pr_number:
            log.warning(f"Skipping benchalerts for {commit_hash}: no PR number found")
            self.mark_finished(comparison=None, check_link=None, pr_comment_link=None)
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
            conbench_client = MockBenchclientsConbenchClient(adapter=adapter)
            github_client = MockBenchalertsGitHubClient(adapter=adapter)
        else:
            conbench_client = None
            github_client = None

        run_ids = [run.id for run in self.benchmarkable.runs]
        log.info(f"Analyzing run IDs: {run_ids}")

        possible_build_urls = [
            run.buildkite_build_web_url
            for run in self.benchmarkable.runs
            if run.machine_name in MACHINES_WITH_PUBLIC_BK_URLS
            and run.buildkite_build_web_url
        ]
        log.info(
            f"Linking to the first in this list if it's nonempty: {possible_build_urls}"
        )
        build_url = possible_build_urls[0] if possible_build_urls else None

        benchalerts_log.setLevel("DEBUG")

        alerter = ArrowAlerter(commit_hash=commit_hash, reason=self.reason)

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
                    alerter=alerter,
                    build_url=build_url,
                ),
                steps.GitHubPRCommentAboutCheckStep(
                    pr_number=pr_number,
                    repo=self.benchmarkable.repo,
                    github_client=github_client,
                    alerter=alerter,
                ),
                # TODO: post to Slack about failures, create GitHub issues?
            ]
        )

        output = pipeline.run_pipeline()
        self.mark_finished(
            comparison=output["z_comparison"],
            check_link=output["GitHubCheckStep"][0]["html_url"],
            pr_comment_link=output["GitHubPRCommentAboutCheckStep"]["html_url"],
        )

    def mark_finished(
        self,
        comparison: Optional[FullComparisonInfo],
        check_link: Optional[str],
        pr_comment_link: Optional[str],
    ) -> None:
        """Mark this run as finished, and save the comparison data."""
        if comparison:
            alerter = ArrowAlerter(commit_hash="doesn't matter", reason=self.reason)
            self.status = alerter.github_check_status(comparison).value
            # We used to do this, but these days this is so big that the BK job is
            # getting OOM killed.
            # self.output = dataclasses.asdict(comparison)
            self.output = {"finished": True}
        if check_link:
            self.check_link = check_link
        if pr_comment_link:
            self.pr_comment_link = pr_comment_link

        self.finished_at = s.sql.func.now()
        self.save()


class MockBenchalertsGitHubClient(GitHubRepoClient):
    """During pytest, bypass the hassle of mocking the GitHub App login."""

    def __init__(self, adapter):
        self._is_github_app_token = True
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.base_url = os.environ["GITHUB_API_BASE_URL"] + "/repos/apache/arrow"


class MockBenchclientsConbenchClient(ConbenchClient):
    """During pytest, bypass the hassle of mocking the Conbench login."""

    def __init__(self, adapter):
        super().__init__()
        self.session.mount("https://", adapter)

    def _login_or_raise(self) -> None:
        pass


class ArrowAlerter(Alerter):
    """Customize messages and logic for this Arrow repo."""

    def __init__(self, commit_hash: str, reason: str) -> None:
        super().__init__()
        self.commit_hash = commit_hash
        self.reason = reason

    def intro_sentence(self, full_comparison: FullComparisonInfo) -> str:
        num_runs = len(full_comparison.run_comparisons)
        s = "" if num_runs == 1 else "s"
        have = "has" if num_runs == 1 else "have"

        if self.reason == "pull-request":
            intro = self.clean(
                f"""
                Thanks for your patience. Conbench analyzed the {num_runs} benchmarking
                run{s} that {have} been run so far on PR commit {self.commit_hash}.
                """
            )
        else:
            intro = self.clean(
                f"""
                After merging your PR, Conbench analyzed the {num_runs} benchmarking
                run{s} that {have} been run so far on merge-commit {self.commit_hash}.
                """
            )

        return intro + "\n\n"

    @staticmethod
    def _is_known_unstable(result_info: dict) -> bool:
        """Whether a benchmark result is known to sometimes produce false positives when
        applying the lookback z-score analysis, and should be treated differently in
        alerts.

        result_info looks like the response from this endpoint:
        https://conbench.ursa.dev/api/redoc#tag/Comparisons/paths/~1api~1compare~1benchmark-results~1%7Bcompare_ids%7D~1/get
        """
        contender = result_info["contender"]
        if not contender:
            return False
        return contender["language"] not in ["Python", "R"]

    def _separate_known_unstable_benchmarks(
        self,
        full_comparison: FullComparisonInfo,
    ) -> Tuple[FullComparisonInfo, FullComparisonInfo]:
        """Separate out certain benchmarks that are known to be unstable, so that we
        alert differently for them.
        """
        stable_comparison = deepcopy(full_comparison)
        unstable_comparison = deepcopy(full_comparison)

        for run in stable_comparison.run_comparisons:
            if run.compare_results:
                run.compare_results = [
                    result
                    for result in run.compare_results
                    if not self._is_known_unstable(result)
                ]

        for run in unstable_comparison.run_comparisons:
            if run.compare_results:
                run.compare_results = [
                    result
                    for result in run.compare_results
                    if self._is_known_unstable(result)
                ]

        return stable_comparison, unstable_comparison

    def github_check_status(self, full_comparison: FullComparisonInfo) -> CheckStatus:
        if self.reason == "pull-request":
            # For PR requests, the check status/title should be based on all possible
            # results since they might be filtered by language.
            return super().github_check_status(full_comparison)

        stable_comparison, _ = self._separate_known_unstable_benchmarks(full_comparison)
        return super().github_check_status(stable_comparison)

    def github_check_title(self, full_comparison: FullComparisonInfo) -> str:
        if self.reason == "pull-request":
            # For PR requests, the check status/title should be based on all possible
            # results since they might be filtered by language.
            return super().github_check_title(full_comparison)

        stable_comparison, _ = self._separate_known_unstable_benchmarks(full_comparison)
        return super().github_check_title(stable_comparison)

    def github_check_summary(
        self, full_comparison: FullComparisonInfo, build_url: Optional[str]
    ) -> str:
        (
            stable_comparison,
            unstable_comparison,
        ) = self._separate_known_unstable_benchmarks(full_comparison)

        summary = super().github_check_summary(stable_comparison, build_url) + "\n\n"

        if unstable_comparison.results_with_errors:
            summary += self.clean(
                """
                ## Unstable benchmarks with errors

                These are errors that were caught while running the known-unstable
                benchmarks. You can click each link to go to the Conbench entry for that
                benchmark, which might have more information about what the error was.
                """
            )
            summary += _list_results(unstable_comparison.results_with_errors)

        if unstable_comparison.results_with_z_regressions:
            summary += self.clean(
                """
                ## Unstable benchmarks with performance regressions

                The following benchmark results indicate a possible performance
                regression, but are known to sometimes produce false positives when
                applying the lookback z-score analysis.
                """
            )
            summary += _list_results(unstable_comparison.results_with_z_regressions)

        return summary

    def github_pr_comment(
        self, full_comparison: FullComparisonInfo, check_link: str
    ) -> str:
        if self.reason == "pull-request":
            # For PR requests, the comment should be based on all possible results since
            # they might be filtered by language.
            return super().github_pr_comment(full_comparison, check_link)

        (
            stable_comparison,
            unstable_comparison,
        ) = self._separate_known_unstable_benchmarks(full_comparison)

        comment = super().github_pr_comment(stable_comparison, check_link)

        if (
            unstable_comparison.results_with_errors
            or unstable_comparison.results_with_z_regressions
        ):
            number = len(unstable_comparison.results_with_errors) + len(
                unstable_comparison.results_with_z_regressions
            )
            ss = "s" if number != 1 else ""
            comment += " "
            comment += self.clean(
                f"""
                It also includes information about {number} possible false positive{ss}
                for unstable benchmarks that are known to sometimes produce them.
                """
            )
            # Don't get too excited about no regressions
            comment.replace(". 🎉", " among the stable benchmarks.")

        return comment
