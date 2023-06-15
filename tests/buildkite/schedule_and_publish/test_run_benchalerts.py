import json
from typing import Optional

import sqlalchemy as s

from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.run_benchalerts import run_benchalerts
from config import Config
from models.benchmarkable import Benchmarkable
from models.run import Run
from tests.helpers import (
    machine_configs,
    make_github_webhook_event_for_comment,
    outbound_requests,
    test_benchmarkable_id,
)

machines = list(machine_configs.keys())


def last_pr_comment_body_posted() -> Optional[str]:
    """Return the body of the last comment posted on the PR, or None if there isn't one."""
    pr_urls = [
        "http://mocked-integrations:9999/github/repos/apache/arrow/issues/1234/comments",
        "http://mocked-integrations:9999/github/repos/apache/arrow/issues/10973/comments",
    ]
    for url, response_data in reversed(outbound_requests):
        if url in pr_urls:
            return json.loads(response_data)["body"]
    return None


def assert_last_pr_comment_was_pending():
    expected_comment_body = (
        f"Benchmark runs are scheduled for commit {test_benchmarkable_id}. "
        f"Watch {Config.CONBENCH_URL} for updates. A comment will be posted "
        "here when the runs are complete."
    )
    assert last_pr_comment_body_posted()
    assert last_pr_comment_body_posted() == expected_comment_body


def assert_last_pr_comment_was_benchalerts_regression():
    assert last_pr_comment_body_posted()
    # Don't check the exact text of the comment because it changes often
    assert "performance regression" in last_pr_comment_body_posted()
    # Ensure there's a link to the posted report (a GitHub Check)
    assert (
        "https://github.com/github/hello-world/runs/4" in last_pr_comment_body_posted()
    )


def assert_no_pr_comment_was_posted():
    assert last_pr_comment_body_posted() is None


def test_run_benchalerts_on_pr_request(client):
    outbound_requests.clear()

    make_github_webhook_event_for_comment(
        client, comment_body="@ursabot please benchmark"
    )
    run_benchalerts()
    assert_last_pr_comment_was_pending()

    # Only finish one of the machines
    for run in Run.all():
        if run.machine_name == machines[0]:
            run.finished_at = s.sql.func.now()
            run.status = "finished"
            run.save()

    run_benchalerts()
    assert_last_pr_comment_was_pending()

    # Finish the other machine
    for run in Run.all():
        if run.machine_name == machines[1]:
            run.finished_at = s.sql.func.now()
            run.status = "finished"
            run.save()

    run_benchalerts()
    assert_last_pr_comment_was_benchalerts_regression()

    # Verify pull comment was marked finished since all runs have status = "finished"
    assert Benchmarkable.get(test_benchmarkable_id).benchalerts_runs[0].finished_at


def test_run_benchalerts_on_merged_pull_requests():
    outbound_requests.clear()

    get_commits()
    contender = Benchmarkable.get("f2f663be0a87e13c9cd5403dea51379deb4cf04d")
    baseline = Benchmarkable.get("c6fdeaf9fb85622242963dc28660e9592088986c")

    # Verify Pull Request is not updated when no runs are finished
    run_benchalerts()
    assert_no_pr_comment_was_posted()

    # Verify Pull Request is not updated when only baseline runs are finished
    for run in baseline.runs:
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()

    run_benchalerts()
    assert_no_pr_comment_was_posted()

    # Verify Pull Request is updated when baseline and contender runs are finished
    for run in contender.runs:
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()

    run_benchalerts()
    assert_last_pr_comment_was_benchalerts_regression()

    assert contender.benchalerts_runs[0].finished_at
