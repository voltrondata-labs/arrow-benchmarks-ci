import json

import sqlalchemy as s

from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.publish_benchmark_alerts_on_pull_requests import (
    publish_benchmark_alerts_on_pull_requests,
)
from models.benchmarkable import Benchmarkable
from tests.helpers import outbound_requests


def test_publish_benchmark_alerts_on_pull_requests(client):
    get_commits()
    contender = Benchmarkable.get("f2f663be0a87e13c9cd5403dea51379deb4cf04d")
    baseline = Benchmarkable.get("c6fdeaf9fb85622242963dc28660e9592088986c")

    # Modify baseline and contender run ids for ursa-i9-9960x so
    # /conbench/api/compare/runs/baseline_run_id...contender_run_id/ url is used to get results
    # from mocked conbench service. Response for /conbench/api/compare/runs/baseline_run_id...contender_run_id/
    # contains benchmarks with z-scores that should trigger "Benchmarks have high level of regressions" alert
    for run in baseline.runs:
        if run.machine_name == "ursa-i9-9960x":
            run.id = "baseline_run_id"
        run.buildkite_data = {"1": "1"}
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()

    for run in contender.runs:
        if run.machine_name == "ursa-i9-9960x":
            run.id = "contender_run_id"
        run.buildkite_data = {"1": "1"}
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()

    publish_benchmark_alerts_on_pull_requests()
    assert (
        outbound_requests[-1][0]
        == f"http://mocked-integrations:9999/github/repos/apache/arrow/issues/{contender.pull_number}/comments"
    )
    print(outbound_requests[-1][1])
    assert json.loads(outbound_requests[-1][1]) == {
        "body": "Benchmarks have high level of regressions"
    }

    assert contender.pull_alert_notification().finished_at
