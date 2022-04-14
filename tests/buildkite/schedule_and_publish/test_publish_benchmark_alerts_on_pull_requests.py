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

    for run in baseline.runs:
        run.buildkite_data = {"1": "1"}
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()

    for run in contender.runs:
        run.id = run.id + "high"
        run.buildkite_data = {"1": "1"}
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()

    publish_benchmark_alerts_on_pull_requests()
    assert 1 == 0
