from copy import deepcopy
from datetime import datetime, timedelta

from buildkite.schedule_and_publish.create_benchmark_builds import (
    create_benchmark_builds,
)
from buildkite.schedule_and_publish.get_commits import get_commits
from buildkite.schedule_and_publish.publish_warnings_on_slack import (
    publish_offline_machine_warnings_on_slack,
    publish_buildkite_build_warnings_on_slack,
)
from models.run import Run


def test_publish_offline_machine_warnings_on_slack():
    # Machine ursa-i9-9960x is always mocked to be offline for all unit tests
    warnings = publish_offline_machine_warnings_on_slack()
    assert warnings == [":warning: ursa-i9-9960x is offline."]


def test_publish_buildkite_build_warnings_on_slack():
    get_commits()
    create_benchmark_builds()

    run = Run.first(machine_name="ursa-i9-9960x", status="scheduled")
    data = deepcopy(run.buildkite_data)
    data["started_at"] = (datetime.utcnow() - timedelta(hours=3)).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    run.buildkite_data = data
    run.save()

    run = Run.first(machine_name="ursa-thinkcentre-m75q", status="scheduled")
    data = deepcopy(run.buildkite_data)
    data["started_at"] = (datetime.utcnow() - timedelta(hours=1)).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    run.buildkite_data = data
    run.save()

    warnings = publish_buildkite_build_warnings_on_slack()
    assert warnings == [
        ":warning: Benchmark build https://buildkite.com/apache-arrow/arrow-bci-benchmark-on-ursa-i9-9960x/builds/1 is running > 2 hours."
    ]
