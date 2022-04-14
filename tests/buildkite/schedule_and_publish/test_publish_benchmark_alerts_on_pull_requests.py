import sqlalchemy as s

from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.publish_benchmark_alerts_on_pull_requests import (
    publish_benchmark_alerts_on_pull_requests,
)
from models.benchmarkable import Benchmarkable
from models.run import Run
from tests.helpers import (
    make_github_webhook_event_for_comment,
    outbound_requests,
    test_benchmarkable_id,
)


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
            == "http://mocked-integrations:9999/github/repos/apache/arrow/issues/comments/1234"
    )

    alert = contender.pull_alert_notification()
    print("message>>>>>>", alert.message)
    assert alert.finished_at
    assert not alert.message
