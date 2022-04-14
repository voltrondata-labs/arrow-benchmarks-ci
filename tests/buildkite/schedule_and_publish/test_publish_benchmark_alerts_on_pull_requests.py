import sqlalchemy as s

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
    make_github_webhook_event_for_comment(
        client, comment_body="@ursabot please benchmark"
    )
    publish_benchmark_alerts_on_pull_requests()
    # Verify new pull comment was not created since no run finished
    assert (
        outbound_requests[-1][0]
        != "http://mocked-integrations:9999/github/repos/apache/arrow/issues/comments/1234"
    )

    i = 1
    for run in Run.all():
        run.id = str(i)
        run.finished_at = s.sql.func.now()
        run.status = "finished"
        run.save()
        i += 1

    publish_benchmark_alerts_on_pull_requests()
    # Verify pull comment was updated
    assert (
        outbound_requests[-1][0]
        == "http://mocked-integrations:9999/github/repos/apache/arrow/issues/comments/1234"
    )

    pull_comment_body = (
        Benchmarkable.get(test_benchmarkable_id)
        .pull_notification()
        .generate_pull_comment_body()
    )
    print(">>>>>>", pull_comment_body)
    assert 1 == 0
