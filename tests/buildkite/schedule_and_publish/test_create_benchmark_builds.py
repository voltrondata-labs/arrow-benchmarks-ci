from buildkite.schedule_and_publish.create_benchmark_builds import (
    create_benchmark_builds,
)
from buildkite.schedule_and_publish.get_commits import get_commits
from models.run import Run
from tests.helpers import machine_configs

machine_already_scheduled_builds_count = {
    "ursa-i9-9960x": 0,
    "ursa-thinkcentre-m75q": 0,
    "new-machine": 1,  # response in tests/mocked_integrations/buildkite/get_scheduled_builds_new_machine.json
}


def test_create_benchmark_builds_no_pull_requests():
    get_commits()

    assert not Run.all(status="scheduled")

    create_benchmark_builds()
    for machine_name, params in machine_configs.items():
        runs = Run.all(machine_name=machine_name, status="scheduled")
        expected_scheduled_builds_count = (
            params["max_builds"] - machine_already_scheduled_builds_count[machine_name]
        )
        assert len(runs) == expected_scheduled_builds_count
        for run in runs:
            assert run.scheduled_at
