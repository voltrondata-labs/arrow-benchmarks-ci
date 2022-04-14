import sqlalchemy as s

from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.publish_benchmark_alerts_on_pull_requests import (
    publish_benchmark_alerts_on_pull_requests,
)
from models.benchmarkable import Benchmarkable
from models.machine import Machine
from models.run import Run
from tests.helpers import (
    machine_configs,
    make_github_webhook_event_for_comment,
    outbound_requests,
    test_baseline_benchmarkable_id,
    test_benchmarkable_id,
)

machines = list(machine_configs.keys())
finished_status = "Finished :arrow_down:33.33% :arrow_up:33.33%"
failed_status = "Failed :arrow_down:33.33% :arrow_up:33.33%"
scheduled_status_with_warning = "Scheduled :warning: ursa-i9-9960x is offline."
skipped_status = "Skipped :warning: Only ['C++', 'Java'] langs are supported on ursa-thinkcentre-m75q"

support_benchmarks_info = """Supported benchmarks:
ursa-i9-9960x: Supported benchmark langs: Python, R, JavaScript
ursa-thinkcentre-m75q: Supported benchmark langs: C++, Java"""


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
